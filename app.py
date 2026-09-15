import os
from flask import Flask, render_template_string

app = Flask(__name__)

GAME_PAGE = r'''<!doctype html>
<html lang="uz">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>NEON RUN — 3D o'yin</title>
  <style>
    :root { color-scheme: dark; --cyan:#55f6ff; --violet:#aa65ff; --ink:#071020; }
    * { box-sizing:border-box; } body { margin:0; overflow:hidden; font-family:Inter,ui-sans-serif,system-ui,sans-serif; background:#030713; color:white; }
    #game { position:fixed; inset:0; } canvas { display:block; width:100%; height:100%; }
    .hud { pointer-events:none; position:fixed; inset:0; padding:clamp(18px,4vw,48px); display:flex; justify-content:space-between; align-items:flex-start; }
    .brand { letter-spacing:.24em; font-size:11px; font-weight:800; color:var(--cyan); text-shadow:0 0 15px #2bd9ff; }
    .brand strong { display:block; margin-top:6px; color:#fff; font-size:clamp(25px,5vw,48px); letter-spacing:-.055em; line-height:.9; }
    .panel { display:flex; gap:12px; } .stat { min-width:100px; padding:12px 15px; border:1px solid #55f6ff55; border-radius:13px; background:#07102099; backdrop-filter:blur(10px); }
    .stat span { color:#9fb4cc; display:block; font-size:10px; font-weight:800; letter-spacing:.12em; } .stat b { font-size:25px; color:var(--cyan); }
    .help { position:fixed; left:50%; bottom:27px; transform:translateX(-50%); text-align:center; color:#c7d8eb; font-size:13px; padding:10px 18px; border-radius:99px; background:#07102099; border:1px solid #ffffff1f; }
    #overlay { position:fixed; inset:0; display:grid; place-items:center; background:radial-gradient(circle at center,#192a6944,#02040eee 70%); transition:.3s; }
    #overlay.hidden { opacity:0; pointer-events:none; } .card { width:min(510px,calc(100% - 36px)); padding:clamp(26px,6vw,52px); text-align:center; border:1px solid #6af5ff66; border-radius:26px; background:linear-gradient(135deg,#0e1a3ee8,#0d0828e8); box-shadow:0 0 55px #4e56e955; }
    .eyebrow { color:var(--cyan); font-size:12px; font-weight:bold; letter-spacing:.2em; } h1 { margin:10px 0; font-size:clamp(45px,10vw,82px); letter-spacing:-.08em; line-height:.86; background:linear-gradient(120deg,#fff,#55f6ff,#b66eff); -webkit-background-clip:text; color:transparent; }
    p { color:#bcd0eb; line-height:1.55; } button { cursor:pointer; margin-top:13px; padding:15px 30px; border:0; border-radius:12px; background:linear-gradient(100deg,#55f6ff,#9d67ff); color:#081027; font-weight:900; font-size:15px; letter-spacing:.05em; box-shadow:0 0 30px #55f6ff77; } button:hover { transform:translateY(-2px); }
    .mobile { display:none; position:fixed; bottom:82px; left:50%; transform:translateX(-50%); gap:45px; } .mobile button { width:64px; height:64px; margin:0; padding:0; border-radius:50%; font-size:25px; opacity:.78; }
    @media (max-width:600px) { .panel{gap:7px}.stat{min-width:76px;padding:9px 11px}.stat b{font-size:20px}.help{bottom:18px;font-size:11px}.mobile{display:flex}.hud{padding:20px}.brand strong{font-size:28px} }
  </style>
</head>
<body>
  <main id="game" aria-label="Neon Run 3D o'yini"></main>
  <section class="hud"><div class="brand">3D ARCADE<strong>NEON RUN</strong></div><div class="panel"><div class="stat"><span>YULDUZLAR</span><b id="score">0</b></div><div class="stat"><span>ENG YAXSHI</span><b id="best">0</b></div></div></section>
  <div class="help">← → yoki A / D bilan harakatlaning · yulduzlarni to'plang</div>
  <div class="mobile"><button id="left" aria-label="Chapga">←</button><button id="right" aria-label="O'ngga">→</button></div>
  <section id="overlay"><div class="card"><div class="eyebrow">KOSMIK YO'LAKKA XUSH KELIBSIZ</div><h1>NEON<br>RUN</h1><p>3D yo'lakda uching, energiya yulduzlarini yig'ing va to'siqlardan qoching. Qancha uzoqqa bora olasiz?</p><button id="start">O'YINNI BOSHLASH</button></div></section>
  <script type="importmap">{"imports":{"three":"https://unpkg.com/three@0.160.1/build/three.module.js"}}</script>
  <script type="module">
    import * as THREE from 'three';
    const scene=new THREE.Scene(), camera=new THREE.PerspectiveCamera(65,innerWidth/innerHeight,.1,150), renderer=new THREE.WebGLRenderer({antialias:true});
    renderer.setSize(innerWidth,innerHeight); renderer.setPixelRatio(Math.min(devicePixelRatio,2)); renderer.setClearColor(0x030713); document.querySelector('#game').append(renderer.domElement);
    scene.fog=new THREE.Fog(0x030713,15,74); camera.position.set(0,5,10); camera.lookAt(0,0,-12);
    scene.add(new THREE.HemisphereLight(0xa9ddff,0x14042b,2)); const light=new THREE.PointLight(0x55f6ff,25,36); light.position.set(0,8,4); scene.add(light);
    const lane=new THREE.Mesh(new THREE.PlaneGeometry(18,150),new THREE.MeshStandardMaterial({color:0x07122c,metalness:.75,roughness:.32})); lane.rotation.x=-Math.PI/2; lane.position.z=-50; scene.add(lane);
    const rails=[]; for(const x of [-4.4,4.4]) { const rail=new THREE.Mesh(new THREE.BoxGeometry(.08,.08,150),new THREE.MeshBasicMaterial({color:0x55f6ff})); rail.position.set(x,.06,-50); scene.add(rail); rails.push(rail); }
    const grid=new THREE.GridHelper(150,45,0x256a9d,0x10284b); grid.position.set(0,.02,-50); scene.add(grid);
    const ship=new THREE.Group(); const body=new THREE.Mesh(new THREE.ConeGeometry(.75,1.9,4),new THREE.MeshStandardMaterial({color:0x92f9ff,emissive:0x13517a,metalness:.7,roughness:.15})); body.rotation.x=-Math.PI/2; ship.add(body); const glow=new THREE.PointLight(0x9d67ff,8,7); glow.position.set(0,0,.4); ship.add(glow); ship.position.set(0,.75,4); scene.add(ship);
    const obstacles=[], stars=[]; const rockGeo=new THREE.IcosahedronGeometry(.7,1), starGeo=new THREE.OctahedronGeometry(.4); const rockMat=new THREE.MeshStandardMaterial({color:0xd73c91,emissive:0x3c092e,roughness:.38}), starMat=new THREE.MeshStandardMaterial({color:0xffe580,emissive:0xff861a,emissiveIntensity:1.5});
    let playing=false, score=0, speed=.34, steer=0, last=0, spawn=0; const scoreEl=document.querySelector('#score'), bestEl=document.querySelector('#best'), overlay=document.querySelector('#overlay'); bestEl.textContent=localStorage.neonBest||0;
    function addItem(type){ const mesh=new THREE.Mesh(type==='star'?starGeo:rockGeo,type==='star'?starMat:rockMat); mesh.position.set((Math.floor(Math.random()*5)-2)*1.65,type==='star'?1.1:.8,-64); mesh.userData.type=type; scene.add(mesh); (type==='star'?stars:obstacles).push(mesh); }
    function reset(){ [...obstacles,...stars].forEach(x=>scene.remove(x)); obstacles.length=stars.length=0; score=0; speed=.34; ship.position.x=0; scoreEl.textContent=0; }
    function finish(){ playing=false; const best=Math.max(score,+localStorage.neonBest||0); localStorage.neonBest=best; bestEl.textContent=best; overlay.querySelector('.eyebrow').textContent='PARVOZ YAKUNLANDI'; overlay.querySelector('h1').innerHTML=`${score}<br>YULDUZ`; overlay.querySelector('p').textContent=`Eng yaxshi natija: ${best}. Yana sinab ko'ring!`; overlay.querySelector('button').textContent='QAYTA O'YNASH'; overlay.classList.remove('hidden'); }
    function start(){ reset(); playing=true; overlay.classList.add('hidden'); }
    document.querySelector('#start').onclick=start; addEventListener('keydown',e=>{if(['ArrowLeft','a','A'].includes(e.key))steer=-1;if(['ArrowRight','d','D'].includes(e.key))steer=1;if(e.key===' '&&!playing)start()}); addEventListener('keyup',()=>steer=0);
    for(const [id,v] of [['left',-1],['right',1]]) { const el=document.querySelector('#'+id); ['pointerdown','pointerup','pointerleave'].forEach(ev=>el.addEventListener(ev,()=>steer=ev==='pointerdown'?v:0)); }
    function loop(t){ requestAnimationFrame(loop); const dt=Math.min((t-last)/16.67,2); last=t; if(playing){ ship.position.x=THREE.MathUtils.clamp(ship.position.x+steer*.16*dt,-3.3,3.3); ship.rotation.z=-steer*.25; speed+=.00012*dt; grid.position.z+=speed*dt; if(grid.position.z>-47) grid.position.z=-50; spawn+=dt; if(spawn>Math.max(20,48-speed*65)){addItem(Math.random()<.57?'star':'rock');spawn=0;} for(const group of [stars,obstacles]) for(let i=group.length-1;i>=0;i--){const o=group[i];o.position.z+=speed*dt;o.rotation.x+=.03*dt;o.rotation.y+=.035*dt;if(o.position.z>8){scene.remove(o);group.splice(i,1);continue}if(Math.abs(o.position.z-ship.position.z)<1.15&&Math.abs(o.position.x-ship.position.x)<.9){if(o.userData.type==='star'){score++;scoreEl.textContent=score;scene.remove(o);group.splice(i,1)}else finish();}} } renderer.render(scene,camera); }
    addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight)}); loop(0);
  </script>
</body></html>'''

@app.route('/')
def index():
    return render_template_string(GAME_PAGE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
