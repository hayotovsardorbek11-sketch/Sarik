import os, sqlite3, re, datetime
from flask import Flask, render_template_string, request, redirect, session, send_from_directory, jsonify, Response, make_response
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "worm_cinema_secret_2026"

# Sayt nomi va sozlamalar
SITE_NAME = "WORM CINEMA"
STORAGE = 'worm_storage'
if not os.path.exists(STORAGE): os.makedirs(STORAGE)

def get_db():
    conn = sqlite3.connect("worm_cinema.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS cinema (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, source TEXT, poster TEXT, views INTEGER DEFAULT 0, likes INTEGER DEFAULT 0)')
        conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, points INTEGER DEFAULT 0)')
        conn.execute('CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY AUTOINCREMENT, movie_id INTEGER, user_name TEXT, text TEXT)')
        conn.execute('CREATE TABLE IF NOT EXISTS likes_log (user_id TEXT, movie_id INTEGER, UNIQUE(user_id, movie_id))')
    conn.commit()

init_db()

# --- MEDIA UZATISH ---
@app.route('/media/<path:filename>')
def media(filename):
    return send_from_directory(STORAGE, filename)

# --- ASOSIY DIZAYN ---
HTML_LAYOUT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ sname }}</title>
    <style>
        body { background:#000; color:#fff; font-family:sans-serif; margin:0; }
        .nav { background:#0a0a0a; padding:15px; border-bottom:2px solid #f00; display:flex; justify-content:space-between; align-items:center; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; padding: 10px; }
        .movie-card { background:#111; border-radius:8px; border:1px solid #222; overflow:hidden; }
        .movie-poster { width:100%; height:200px; object-fit:cover; cursor:pointer; background:#222; }
        .movie-title { padding:8px; font-size:13px; font-weight:bold; text-align:center; }
        
        /* Modal - Pastdan parda ochilishi */
        #modal { display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.95); z-index:1000; overflow-y:auto; }
        .modal-body { max-width:600px; margin: 40px auto 0; background:#050505; border-top:3px solid #f00; border-radius:15px 15px 0 0; }
        video { width:100%; background:#000; }
        .p-20 { padding:20px; }
        .close-btn { color:#f00; font-size:40px; float:right; padding:10px; cursor:pointer; }
        .btn-like { background:#f00; border:none; color:#000; padding:10px 20px; font-weight:bold; border-radius:25px; cursor:pointer; }
        .comm-input { width:70%; padding:12px; background:#1a1a1a; border:1px solid #333; color:#fff; border-radius:5px; }
    </style>
</head>
<body>
    <div class="nav">
        <b style="color:#f00; font-size:20px;">{{ sname }} 🎬</b>
        <span style="color:#0f0;">💰 {{ points }} Ball</span>
        {% if session['user'] == 'Sardorbeko008' %} <a href="/admin" style="color:yellow; text-decoration:none; font-size:12px;">ADMIN</a> {% endif %}
    </div>

    <div class="grid">
        {% for m in movies %}
        <div class="movie-card">
            <img src="/media/{{ m.poster }}" class="movie-poster" 
                 onclick="openMovie('{{ m.id }}', '{{ m.title }}', '{{ m.source }}', '{{ m.likes }}', '{{ m.views }}')">
            <div class="movie-title">{{ m.title }}</div>
        </div>
        {% endfor %}
    </div>

    <div id="modal">
        <div class="modal-body">
            <span class="close-btn" onclick="closeMovie()">&times;</span>
            <div style="clear:both;"></div>
            <video id="v-player" controls playsinline></video>
            <div class="p-20">
                <h2 id="v-title" style="margin-top:0;"></h2>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <button class="btn-like" onclick="doLike()">❤️ <span id="v-likes"></span></button>
                    <span id="v-views" style="color:#666; font-size:14px;"></span>
                </div>
                <hr border="0" style="height:1px; background:#222; margin:25px 0;">
                <b>Fikrlar:</b>
                <div id="c-list" style="margin-top:15px; font-size:14px; color:#ccc;"></div>
                <div style="margin-top:15px; display:flex; gap:8px;">
                    <input id="c-text" class="comm-input" placeholder="Moment yozing...">
                    <button onclick="sendComm()" style="background:#0f0; border:none; padding:10px 20px; border-radius:5px; font-weight:bold;">OK</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentId = null;

        function openMovie(id, title, source, likes, views) {
            currentId = id;
            document.getElementById('v-title').innerText = title;
            document.getElementById('v-likes').innerText = likes;
            document.getElementById('v-views').innerText = views + " marta ko'rildi";
            
            let v = document.getElementById('v-player');
            v.src = "/media/" + source;
            v.load();
            v.play();

            document.getElementById('modal').style.display = 'block';
            loadComments(id);
            fetch('/view/' + id);
        }

        function closeMovie() {
            document.getElementById('modal').style.display = 'none';
            document.getElementById('v-player').pause();
            document.getElementById('v-player').src = "";
        }

        function loadComments(id) {
            fetch('/get_comments/' + id).then(r=>r.json()).then(data => {
                let list = document.getElementById('c-list');
                list.innerHTML = data.length ? '' : 'Fikrlar yo'q...';
                data.forEach(c => {
                    list.innerHTML += `<div style="margin-bottom:10px;"><b style="color:#0f0;">${c.user}:</b> ${c.text}</div>`;
                });
            });
        }

        function doLike() {
            fetch('/like/' + currentId).then(r=>r.json()).then(d => {
                if(d.ok) document.getElementById('v-likes').innerText = parseInt(document.getElementById('v-likes').innerText) + 1;
            });
        }

        function sendComm() {
            let t = document.getElementById('c-text').value;
            if(!t) return;
            fetch('/comment', {
                method:'POST',
                headers:{'Content-Type':'application/x-www-form-urlencoded'},
                body: `id=${currentId}&t=${t}`
            }).then(() => { document.getElementById('c-text').value=''; loadComments(currentId); });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    un = request.cookies.get('worm_user')
    if un: session['user'] = un
    if 'user' not in session: return redirect('/login')
    conn = get_db()
    movies = conn.execute("SELECT * FROM cinema ORDER BY id DESC").fetchall()
    user = conn.execute("SELECT points FROM users WHERE name = ?", (session['user'],)).fetchone()
    conn.close()
    return render_template_string(HTML_LAYOUT, movies=movies, points=user['points'] if user else 0, sname=SITE_NAME)

@app.route('/login')
def login():
    return f'<body style="background:#000;color:#f00;text-align:center;padding-top:100px;font-family:sans-serif;"><h1>{SITE_NAME}</h1><form action="/auth" method="POST"><input name="un" placeholder="Ismingiz..." required style="padding:10px; width:200px;"><br><br><button style="padding:10px 40px; background:#f00; border:none; color:#000; font-weight:bold;">KIRISH</button></form></body>'

@app.route('/auth', methods=['POST'])
def auth():
    un = request.form.get('un', '').strip()
    session['user'] = un
    conn = get_db()
    try: conn.execute("INSERT INTO users (name, points) VALUES (?, 0)", (un,)); conn.commit()
    except: pass
    conn.close()
    resp = make_response(redirect('/'))
    resp.set_cookie('worm_user', un, max_age=31536000)
    return resp

@app.route('/admin')
def admin():
    if session.get('user') != 'Sardorbeko008': return "Taqiqlangan", 403
    return f'''<body style="background:#000;color:#fff;padding:20px;font-family:sans-serif;">
    <h2>{SITE_NAME} - ADMIN PANEL</h2>
    <form action="/upload" method="POST" enctype="multipart/form-data">
        Kino nomi: <br><input name="t" required style="width:100%; padding:10px;"><br><br>
        Video fayl: <br><input type="file" name="v_f" required><br><br>
        Muqova (Rasm): <br><input type="file" name="p_f" required><br><br>
        <button style="background:green; color:white; padding:15px; border:none; width:100%; font-weight:bold;">YUKLASH</button>
    </form><br><hr><br><a href="/" style="color:red;">SAYTGA QAYTISH</a></body>'''

@app.route('/upload', methods=['POST'])
def upload():
    t, v_f, p_f = request.form['t'], request.files.get('v_f'), request.files.get('p_f')
    if v_f and p_f and session.get('user') == 'Sardorbeko008':
        v_name = secure_filename(v_f.filename)
        p_name = secure_filename(p_f.filename)
        v_f.save(os.path.join(STORAGE, v_name))
        p_f.save(os.path.join(STORAGE, p_name))
        conn = get_db()
        conn.execute("INSERT INTO cinema (title, source, poster) VALUES (?,?,?)", (t, v_name, p_name))
        conn.commit(); conn.close()
    return redirect('/')

@app.route('/get_comments/<int:mid>')
def get_comments(mid):
    conn = get_db()
    c = conn.execute("SELECT user_name, text FROM comments WHERE movie_id = ? ORDER BY id DESC", (mid,)).fetchall()
    conn.close()
    return jsonify([{'user': i['user_name'], 'text': i['text']} for i in c])

@app.route('/comment', methods=['POST'])
def comment():
    mid, txt = request.form['id'], request.form['t'].strip()
    if mid and txt and 'user' in session:
        conn = get_db()
        conn.execute("INSERT INTO comments (movie_id, user_name, text) VALUES (?,?,?)", (mid, session['user'], txt))
        conn.commit(); conn.close()
    return "ok"

@app.route('/like/<int:id>')
def like(id):
    u = session.get('user')
    conn = get_db()
    try:
        conn.execute("INSERT INTO likes_log (user_id, movie_id) VALUES (?,?)", (u, id))
        conn.execute("UPDATE cinema SET likes = likes + 1 WHERE id = ?", (id,))
        conn.execute("UPDATE users SET points = points + 1 WHERE name = ?", (u,))
        conn.commit(); return jsonify({"ok": True})
    except: return jsonify({"ok": False})
    finally: conn.close()

@app.route('/view/<int:id>')
def view(id):
    conn = get_db()
    try: conn.execute("UPDATE users SET points = points + 2 WHERE name = ?", (session.get('user'),))
    except: pass
    conn.execute("UPDATE cinema SET views = views + 1 WHERE id = ?", (id,)); conn.commit(); conn.close()
    return "ok"

if __name__ == '__main__':
    # Railway PORT ni avtomatik beradi
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
