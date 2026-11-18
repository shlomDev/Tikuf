import json,base64,glob
d=json.load(open('d.json'));fs=sorted(glob.glob('f*.jpg'))
im=['data:image/jpeg;base64,'+base64.b64encode(open(f,'rb').read()).decode() for f in fs]
h='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>Gap Counter – live tracking demo</title><meta name="color-scheme" content="light dark">
<style>
:root{--bg:#eef1ee;--s:#fff;--ink:#15201e;--mut:#5b6b68;--t:#0a6b66;--a:#b86e00;--r:#b3261e;--ln:#d3dbd8;box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
@media(prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#101615;--s:#192220;--ink:#e6efec;--mut:#93a5a1;--t:#4cc3bb;--a:#e8a23a;--r:#ff8a80;--ln:#2b3836}}
*{box-sizing:border-box}html,body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 "IBM Plex Sans",system-ui,sans-serif}
main{max-width:760px;margin:0 auto;padding:14px}h1{font-size:20px;margin:4px 0 2px}p.s{margin:0 0 12px;color:var(--mut);font-size:13px}
.v{position:relative;border-radius:10px;overflow:hidden;background:#000}.v img{display:block;width:100%}
.bar{display:flex;gap:8px;align-items:center;margin:10px 0}button{font:inherit;background:var(--t);color:var(--bg);border:0;border-radius:8px;padding:8px 14px;cursor:pointer}button:focus-visible,input:focus-visible{outline:3px solid var(--a)}
input[type=range]{flex:1;accent-color:var(--t)}
.g{display:grid;grid-template-columns:repeat(2,1fr);gap:8px}@media(min-width:560px){.g{grid-template-columns:repeat(4,1fr)}}
.k{background:var(--s);border:1px solid var(--ln);border-radius:10px;padding:10px 12px}.k b{display:block;font-size:28px;line-height:1.1;font-variant-numeric:tabular-nums}.k span{color:var(--mut);font-size:12.5px}
.k.gap b{color:var(--a)}canvas{width:100%;height:120px;background:var(--s);border:1px solid var(--ln);border-radius:10px;margin-top:8px;display:block}
.n{font-size:12.5px;color:var(--mut);margin-top:10px}.n b{color:var(--ink)}
</style></head><body><main>
<h1>People tracking and boarding gap</h1><p class="s">Real YOLOX detection and tracking on a sample pedestrian clip. Each person gets an anonymous ID. Orange line = the “door”.</p>
<div class="v"><img id="im" alt="Annotated video frame with tracked people"></div>
<div class="bar"><button id="pl">Pause</button><input id="sc" type="range" min="0" value="0" aria-label="Timeline"></div>
<div class="g"><div class="k"><b id="a">0</b><span>people in frame</span></div><div class="k"><b id="u">0</b><span>unique IDs so far</span></div><div class="k"><b id="b">0</b><span>crossed line inward</span></div><div class="k"><b id="vv">0</b><span>validations (simulated)</span></div></div>
<div class="g" style="margin-top:8px"><div class="k gap" style="grid-column:1/-1"><b id="gp">0</b><span>estimated unvalidated boardings (inward crossings older than __GR__ s with no validation)</span></div></div>
<canvas id="c" width="720" height="120"></canvas>
<p class="n"><b>Measured:</b> __FR__ frames at __PF__ FPS on CPU, ONNX nano model, __ID__ IDs assigned. <b>Not measured:</b> counting accuracy, because this clip has no hand-counted ground truth. The detector misses small, distant people. <b>Simulated:</b> 70% of inward crossings get a fake validation 1–10 s later. No faces, no images stored beyond this demo.</p>
</main><script>
const D=__D__,IM=__IM__,S=2,fps=D.fps,gr=D.grace;let i=0,play=1,tm;
const $=x=>document.getElementById(x),sc=$('sc');sc.max=IM.length-1;
const cv=$('c'),cx=cv.getContext('2d');
function st(k){return getComputedStyle(document.documentElement).getPropertyValue(k)}
function draw(){const F=D.F,n=F.length,W=cv.width,H=cv.height,mx=Math.max(1,...F.map(f=>f.B));cx.clearRect(0,0,W,H);
const L=(k,c,fn)=>{cx.strokeStyle=st(c);cx.lineWidth=2;cx.beginPath();F.forEach((f,j)=>{const x=j/n*W,y=H-8-(fn(f,j)/mx)*(H-20);j?cx.lineTo(x,y):cx.moveTo(x,y)});cx.stroke()};
L(0,'--t',f=>f.B);L(0,'--a',f=>f.V);cx.strokeStyle=st('--mut');cx.lineWidth=1;const px=Math.min(i*S,n-1)/n*W;cx.beginPath();cx.moveTo(px,0);cx.lineTo(px,H);cx.stroke();
cx.fillStyle=st('--t');cx.font='12px system-ui';cx.fillText('inward crossings',8,14);cx.fillStyle=st('--a');cx.fillText('validations',120,14)}
function show(){const j=Math.min(i*S,D.F.length-1),f=D.F[j],o=D.F[Math.max(0,j-gr)];$('im').src=IM[i];sc.value=i;
$('a').textContent=f.n;$('u').textContent=f.U;$('b').textContent=f.B;$('vv').textContent=f.V;$('gp').textContent=Math.max(0,o.B-f.V);draw()}
function loop(){if(play){i=(i+1)%IM.length;show()}tm=setTimeout(loop,1000/fps*S)}
$('pl').onclick=()=>{play=!play;$('pl').textContent=play?'Pause':'Play'};sc.oninput=()=>{i=+sc.value;show()};
matchMedia('(prefers-color-scheme:dark)').onchange=draw;show();loop();
</script></body></html>'''
h=h.replace('__D__',json.dumps(d)).replace('__IM__',json.dumps(im)).replace('__GR__',str(round(d['grace']/d['fps']))).replace('__FR__',str(d['frames'])).replace('__PF__',str(round(d['proc_fps']))).replace('__ID__',str(d['ids']))
open('gap-counter-demo.html','w').write(h);print(len(h)//1024,'KB')
