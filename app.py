import os, sqlite3, datetime
from flask import Flask, render_template_string, request, redirect, session, jsonify, make_response

app = Flask(__name__)
app.secret_key = "worm_cinema_final_fix_2026"

SITE_NAME = "WORM CINEMA"

def get_db():
    conn = sqlite3.connect("worm_cinema_v37.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS cinema (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, source TEXT, views INTEGER DEFAULT 0, likes INTEGER DEFAULT 0)')
        conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, points INTEGER DEFAULT 0)')
        conn.execute('CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY AUTOINCREMENT, movie_id INTEGER, user_name TEXT, text TEXT)')
        conn.execute('CREATE TABLE IF NOT EXISTS likes_log (user_id TEXT, movie_id INTEGER, UNIQUE(user_id, movie_id))')
    conn.commit()

init_db()

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
        .nav { background:#0a0a0a; padding:15px; border-bottom:2px solid #f00; display:flex; justify-content:space-between; align-items:center; position:sticky; top:0; z-index:100; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; padding: 10px; }
        .movie-card { background:#111; border-radius:8px; border:1px solid #222; overflow:hidden; cursor:pointer; }
        video.preview { width:100%; height:180px; object-fit:cover; pointer-events:none; background:#222; }
        .movie-title { padding:8px; font-size:13px; font-weight:bold; text-align:center; color:#eee; }
        #modal { display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.98); z-index:1000; overflow-y:auto; }
        .modal-body { max-width:600px; margin: 20px auto; background:#050505; border-top:3px solid #f00; border-radius:15px; }
        video#main-v { width:100%; border-radius:15px 15px 0 0; }
        .p-20 { padding:20px; }
        .close-btn { color:#f00; font-size:40px; float:right; padding:10px; cursor:pointer; font-weight:bold; }
        .btn-like { background:#f00; border:none; color:#000; padding:10px 20px; font-weight:bold; border-radius:25px; cursor:pointer; }
        .comm-input { width:70%; padding:12px; background:#1a1a1a; border:1px solid #333; color:#fff; border-radius:5px; }
    </style>
</head>
<body>
    <div class="nav">
        <b style="color:#f00; font-size:18px;">{{ sname }} 🎬</b>
        <span style="color:#0f0; font-size:14px;">💰 {{ points }} Ball</span>
        {% if session['user'] == 'Sardorbeko008' %} <a href="/admin" style="color:yellow; text-decoration:none;">[ADMIN]</a> {% endif %}
    </div>
    <div class="grid">
        {% for m in movies %}
        <div class="movie-card" onclick="openMovie('{{ m.id }}', '{{ m.title }}', '{{ m.source }}', '{{ m.likes }}', '{{ m.views }}')">
            <video class="preview" preload="metadata" crossorigin="anonymous">
                <source src="{{ m.source }}" type="video/mp4">
            </video>
            <div class="movie-title">{{ m.title }}</div>
        </div>
        {% endfor %}
    </div>
    <div id="modal">
        <div class="modal-body">
            <span class="close-btn" onclick="closeMovie()">&times;</span>
            <div style="clear:both;"></div>
            <video id="main-v" controls playsinline crossorigin="anonymous"></video>
            <div class="p-20">
                <h2 id="v-title" style="margin:0 0 15px 0; font-size:18px;"></h2>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <button class="btn-like" onclick="doLike()">❤️ <span id="v-likes"></span></button>
                    <span id="v-views" style="color:#666; font-size:12px;"></span>
                </div>
                <hr style="border:0; height:1px; background:#222; margin:20px 0;">
                <div id="c-list" style="margin-bottom:15px; font-size:14px;"></div>
                <div style="display:flex; gap:8px;">
                    <input id="c-text" class="comm-input" placeholder="Fikr yozing...">
                    <button onclick="sendComm()" style="background:#0f0; border:none; padding:10px; border-radius:5px; font-weight:bold;">OK</button>
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
            document.getElementById('v-views').innerText = views + " ko'rildi";
            let v = document.getElementById('main-v');
            v.src = source;
            v.load(); v.play();
            document.getElementById('modal').style.display = 'block';
            loadComments(id);
            fetch('/view/' + id);
        }
        function closeMovie() {
            document.getElementById('modal').style.display = 'none';
            document.getElementById('main-v').pause();
            document.getElementById('main-v').src = "";
        }
        function loadComments(id) {
            fetch('/get_comments/' + id).then(r=>r.json()).then(data => {
                let list = document.getElementById('c-list');
                list.innerHTML = data.map(c => `<div style="margin-bottom:8px;"><b style="color:#0f0;">${c.user}:</b> ${c.text}</div>`).join('');
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
                body: `id=${currentId}&t=${encodeURIComponent(t)}`
            }).then(() => { document.getElementById('c-text').value=''; loadComments(currentId); });
        }
    </script>
</body>
</html>
"""

# --- BACKEND LOGIKA ---

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
    return f'<body style="background:#000;color:#f00;text-align:center;padding-top:100px;font-family:sans-serif;"><h1>{SITE_NAME}</h1><form action="/auth" method="POST"><input name="un" required placeholder="Ism..." style="padding:10px;"><br><br><button style="padding:10px 20px;">KIRISH</button></form></body>'

@app.route('/auth', methods=['POST'])
def auth():
    un = request.form.get('un', '').strip()
    session['user'] = un
    conn = get_db(); conn.execute("INSERT OR IGNORE INTO users (name, points) VALUES (?, 0)", (un,)); conn.commit(); conn.close()
    resp = make_response(redirect('/'))
    resp.set_cookie('worm_user', un, max_age=31536000); return resp

@app.route('/admin')
def admin():
    if session.get('user') != 'Sardorbeko008': return "Ruxsat yo'q", 403
    conn = get_db(); movies = conn.execute("SELECT * FROM cinema ORDER BY id DESC").fetchall(); conn.close()
    m_list = "".join([f'<div style="border-bottom:1px solid #333; padding:10px;">{m["title"]} <a href="/delete/{m["id"]}" style="color:red; float:right;">[O`CHIRISH]</a></div>' for m in movies])
    return f'''<body style="background:#000;color:#fff;padding:20px;font-family:sans-serif;">
    <h2>ADMIN PANEL</h2>
    <form action="/add_movie" method="POST" style="background:#111; padding:15px; border-radius:10px;">
        Kino nomi: <br><input name="t" required style="width:100%; padding:10px; margin-bottom:10px;"><br>
        Video Link (.mp4): <br><input name="s" required style="width:100%; padding:10px; margin-bottom:10px;" placeholder="https://...mp4"><br>
        <button style="background:green; color:white; padding:15px; width:100%; border:none; font-weight:bold;">QO`SHISH</button>
    </form>
    <br><h3>KINOLAR</h3><div style="background:#111; border-radius:10px; padding:10px;">{m_list}</div>
    <br><a href="/" style="color:cyan;">SAYTGA QAYTISH</a></body>'''

@app.route('/add_movie', methods=['POST'])
def add_movie():
    if session.get('user') == 'Sardorbeko008':
        t, s = request.form['t'], request.form['s']
        conn = get_db(); conn.execute("INSERT INTO cinema (title, source) VALUES (?,?)", (t, s)); conn.commit(); conn.close()
    return redirect('/admin')

@app.route('/delete/<int:id>')
def delete(id):
    if session.get('user') == 'Sardorbeko008':
        conn = get_db(); conn.execute("DELETE FROM cinema WHERE id = ?", (id,)); conn.commit(); conn.close()
    return redirect('/admin')

@app.route('/get_comments/<int:mid>')
def get_comments(mid):
    conn = get_db(); c = conn.execute("SELECT user_name, text FROM comments WHERE movie_id = ? ORDER BY id DESC", (mid,)).fetchall(); conn.close()
    return jsonify([{'user': i['user_name'], 'text': i['text']} for i in c])

@app.route('/comment', methods=['POST'])
def comment():
    mid, txt = request.form['id'], request.form['t']
    if 'user' in session:
        conn = get_db(); conn.execute("INSERT INTO comments (movie_id, user_name, text) VALUES (?,?,?)", (mid, session['user'], txt)); conn.commit(); conn.close()
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
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
