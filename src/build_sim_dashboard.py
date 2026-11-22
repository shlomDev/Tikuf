import json
R=json.load(open('r.json'));fr=json.load(open('fr.json'))
pc=lambda x:f"{round(x*100)}%"
rows=''.join(f"<tr><td>{n}</td><td>{pc(r['precision'])}</td><td>{pc(r['cover'])}</td><td>{r['mae']:.2f}</td></tr>" for n,r in (('No camera errors',R['clean']),('3% missed / 3% double count',R['res']),('8% missed / 8% double count',R['rough'])))
h='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>Bus boarding simulation – no-tap flagging</title><meta name="color-scheme" content="light dark">
<style>
:root{--bg:#eef1ee;--s:#fff;--ink:#15201e;--mut:#5b6b68;--t:#0a6b66;--a:#b86e00;--r:#b3261e;--ln:#d3dbd8;box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
@media(prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#101615;--s:#192220;--ink:#e6efec;--mut:#93a5a1;--t:#4cc3bb;--a:#e8a23a;--r:#ff8a80;--ln:#2b3836}}
*{box-sizing:border-box}html,body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 "IBM Plex Sans",system-ui,sans-serif}
main{max-width:760px;margin:0 auto;padding:14px}h1{font-size:20px;margin:4px 0 2px}h2{font-size:15px;margin:18px 0 6px}p.s{margin:0 0 12px;color:var(--mut);font-size:13px}
.v{border-radius:10px;overflow:hidden;background:#000}.v img{display:block;width:100%}
.bar{display:flex;gap:8px;align-items:center;margin:10px 0}button{font:inherit;background:var(--t);color:var(--bg);border:0;border-radius:8px;padding:8px 14px;cursor:pointer}button:focus-visible,input:focus-visible{outline:3px solid var(--a)}input[type=range]{flex:1;accent-color:var(--t)}
.g{display:grid;grid-template-columns:repeat(2,1fr);gap:8px}@media(min-width:560px){.g{grid-template-columns:repeat(4,1fr)}}
.k{background:var(--s);border:1px solid var(--ln);border-radius:10px;padding:10px 12px}.k b{display:block;font-size:28px;line-height:1.1;font-variant-numeric:tabular-nums}.k span{color:var(--mut);font-size:12.5px}.k.f b{color:var(--r)}
ul{list-style:none;margin:0;padding:0}li.g{border-left-color:var(--a)}li{background:var(--s);border:1px solid var(--ln);border-left:4px solid var(--r);border-radius:8px;padding:7px 10px;margin-bottom:6px;font-size:13.5px}li small{color:var(--mut)}
.e{color:var(--mut);font-size:13px}table{width:100%;border-collapse:collapse;background:var(--s);border:1px solid var(--ln);border-radius:10px;overflow:hidden;font-size:13.5px}td,th{padding:7px 10px;text-align:left;border-bottom:1px solid var(--ln)}th{color:var(--mut);font-weight:500}
.n{font-size:12.5px;color:var(--mut);margin-top:10px}.n b{color:var(--ink)}
</style></head><body><main>
<h1>Boarding simulation: flag every boarding with no tap</h1><p class="s">Synthetic top-down bus. Each passenger enters, taps the Rav-Kav validator on the pole (or doesn’t), sits, then exits. The system flags a boarding when no tap is matched within __GR__ s. Red = flagged. Amber = one of several boardings had no tap but the system can’t tell which.</p>
<div class="v"><img id="im" alt="Simulated bus with passengers and validator"></div>
<div class="bar"><button id="pl">Pause</button><input id="sc" type="range" min="0" value="0" aria-label="Timeline"></div>
<div class="g"><div class="k"><b id="b">0</b><span>boardings detected</span></div><div class="k"><b id="v">0</b><span>taps received</span></div><div class="k"><b id="a">0</b><span>passengers exited</span></div><div class="k f"><b id="f">0</b><span>boardings with no tap</span></div></div>
<h2>Flag log</h2><ul id="lg"></ul><p class="e" id="em">No flags yet.</p>
<h2>Does the logic hold up? (300 random simulated rides each, about 3 non-payers per ride)</h2>
<table><tr><th>Scenario</th><th>Confident flags that were right</th><th>Evaders flagged or narrowed to a pair</th><th>Avg count error per ride</th></tr>__ROWS__</table>
<p class="n"><b>What this proves:</b> the matching logic and the flagging flow, with exact ground truth. <b>What it does not prove:</b> that the camera detector works on a real bus (that needs real footage) or that real validator data is available. Taps made on a phone app have no position, so when two people board close together the system reports the pair instead of guessing. With a perfect camera the count per ride is exact. The remaining errors come from assumed camera mistakes (missed and double-counted boardings), which must be measured on real footage. Evader rate (25%) and app-tap share (15%) are assumptions.<br><br><b>Privacy:</b> a flag is an event (time, door, ride), not a person. No faces, no images stored. Its use is to direct inspectors and collect statistics. Fining individuals from video needs a legal review.</p>
</main><script>
const IM=__IM__,C=__C__,LG=__LG__,E=__E__;let i=0,play=1;const $=x=>document.getElementById(x),sc=$('sc');sc.max=IM.length-1;
function show(){const c=C[i],t=i*E;$('im').src=IM[i];sc.value=i;$('b').textContent=c.B;$('v').textContent=c.V;$('a').textContent=c.A;$('f').textContent=c.F;
const L=LG.filter(x=>x.t<=t);$('lg').innerHTML=L.map(x=>`<li class="${x.ids.length>1?'g':''}">${x.ids.length>1?x.k+' of '+x.ids.length+' boardings had no tap (#'+x.ids.join(', #')+'): cannot tell which':(x.d?'Possible double count':'No tap detected')+' · passenger #'+x.ids[0]} · <small>flagged at ${x.t.toFixed(1)} s</small></li>`).join('');$('em').style.display=L.length?'none':'block'}
function loop(){if(play){i=(i+1)%IM.length;show()}setTimeout(loop,E*1000)}
$('pl').onclick=()=>{play=!play;$('pl').textContent=play?'Pause':'Play'};sc.oninput=()=>{i=+sc.value;show()};show();loop();
</script></body></html>'''
h=h.replace('__IM__',json.dumps(fr)).replace('__C__',json.dumps(R['ct'])).replace('__LG__',json.dumps(R['log'])).replace('__E__',str(R['every'])).replace('__ROWS__',rows).replace('__GR__','8')
open('bus-simulation-demo.html','w').write(h);print(len(h)//1024,'KB')
