import cv2,numpy as np,onnxruntime as ort,json,time,sys,random,os
from scipy.optimize import linear_sum_assignment
SRC,LY=sys.argv[1],float(sys.argv[2])
CR=sys.argv[4] if len(sys.argv)>4 else 'full'   # full | left | right (side-by-side dual-camera video)
OUT=sys.argv[5] if len(sys.argv)>5 else 'd.json'
IOU1=float(os.environ.get('IOU1',0.15));MISS_S=float(os.environ.get('MISS_S',2));CONF=int(os.environ.get('CONF',3));MINH=float(os.environ.get('MINH',0.12))
ss=ort.InferenceSession(os.environ.get('MODEL','m.onnx')); inn=ss.get_inputs()[0].name; S=int(ss.get_inputs()[0].shape[2])
g=[];st=[]
for s in (8,16,32):
    n=S//s; x,y=np.meshgrid(np.arange(n),np.arange(n)); g.append(np.stack((x,y),2).reshape(-1,2)); st.append(np.full((n*n,1),s))
g=np.concatenate(g).astype(np.float32); st=np.concatenate(st).astype(np.float32)
def det(f):
    h,w=f.shape[:2]; r=min(S/h,S/w); im=cv2.resize(f,(int(w*r),int(h*r)))
    p=np.full((S,S,3),114,np.uint8); p[:im.shape[0],:im.shape[1]]=im
    o=ss.run(None,{inn:p.transpose(2,0,1)[None].astype(np.float32)})[0][0]
    xy=(o[:,:2]+g)*st; wh=np.exp(o[:,2:4])*st; sc=o[:,4]*o[:,5]
    k=sc>0.15; xy,wh,sc=xy[k],wh[k],sc[k]
    b=np.concatenate([xy-wh/2,wh],1)/r
    i=cv2.dnn.NMSBoxes(b.tolist(),sc.tolist(),0.15,0.45)
    i=np.array(i).flatten().astype(int)
    return [(b[j][0],b[j][1],b[j][0]+b[j][2],b[j][1]+b[j][3],float(sc[j])) for j in i]
def iou(a,b):
    x1,y1=max(a[0],b[0]),max(a[1],b[1]);x2,y2=min(a[2],b[2]),min(a[3],b[3])
    i=max(0,x2-x1)*max(0,y2-y1);u=(a[2]-a[0])*(a[3]-a[1])+(b[2]-b[0])*(b[3]-b[1])-i
    return i/u if u>0 else 0
class T:
    n=0
    def __init__(s,d): s.b=list(d[:4]);s.v=[0,0,0,0];s.hits=1;s.miss=0;s.id=None;s.prev=None
    def pred(s): return [s.b[i]+s.v[i] for i in range(4)]
    def upd(s,d):
        nb=list(d[:4]);s.v=[0.6*s.v[i]+0.4*(nb[i]-s.b[i]) for i in range(4)];s.b=nb;s.hits+=1;s.miss=0
def match(ts,ds,th):
    if not ts or not ds: return [],list(range(len(ts))),list(range(len(ds)))
    M=np.array([[1-iou(t.pred(),d) for d in ds] for t in ts]);r,c=linear_sum_assignment(M)
    m=[(i,j) for i,j in zip(r,c) if M[i,j]<1-th]
    return m,[i for i in range(len(ts)) if i not in [a for a,_ in m]],[j for j in range(len(ds)) if j not in [b for _,b in m]]
cap=cv2.VideoCapture(SRC);fps=cap.get(5) or 25;MISS=int(MISS_S*fps) if MISS_S else 20;tracks=[];F=[];ev=[];fr=0;t0=time.time();seen=set();trail={}
rnd=random.Random(7);vals=[]
while True:
    ok,f=cap.read()
    if not ok: break
    if CR!='full':
        w2=f.shape[1]//2;f=f[:,:w2] if CR=='left' else f[:,w2:]
    H,W=f.shape[:2];ly=LY*H
    ds=[d for d in det(f) if d[4]>0.15 and (d[3]-d[1])>MINH*H]
    hi=[d for d in ds if d[4]>=0.4];lo=[d for d in ds if d[4]<0.4]
    m,ut,ud=match(tracks,hi,IOU1)
    for i,j in m: tracks[i].upd(hi[j])
    rest=[tracks[i] for i in ut];m2,ut2,_=match(rest,lo,0.4)
    for i,j in m2: rest[i].upd(lo[j])
    um=set(id(rest[i]) for i in ut2)
    for t in tracks:
        if id(t) in um: t.miss+=1;t.b=t.pred()
    for j in ud:
        if hi[j][4]>0.5: tracks.append(T(hi[j]))
    tracks=[t for t in tracks if t.miss<=MISS]
    inn_=out=0;boxes=[]
    for t in tracks:
        if t.hits>=CONF and t.id is None: T.n+=1;t.id=T.n
        if t.id is None or t.miss>0: continue
        cy=t.b[3];cx=(t.b[0]+t.b[2])/2
        trail.setdefault(t.id,[]).append((int(cx),int(cy)));seen.add(t.id)
        if t.prev is not None:
            if t.prev<ly<=cy: ev.append(('B',fr,t.id))
            elif t.prev>=ly>cy: ev.append(('A',fr,t.id))
        t.prev=cy;boxes.append((t.id,t.b))
    for e in ev:
        if e[0]=='B' and e[1]==fr and rnd.random()<0.7: vals.append(fr+int(rnd.uniform(1,10)*fps))
    v=f.copy()
    for k,tr in trail.items():
        if any(k==b[0] for b in boxes):
            for a,b in zip(tr[-25:],tr[-24:]): cv2.line(v,a,b,(255,200,0),1)
    for i,b in boxes:
        x1,y1,x2,y2=map(int,b);cv2.rectangle(v,(x1,y1),(x2,y2),(60,200,90),2);cv2.putText(v,f'#{i}',(x1,max(12,y1-4)),0,0.55,(255,255,255),2);cv2.putText(v,f'#{i}',(x1,max(12,y1-4)),0,0.55,(20,20,20),1)
    cv2.line(v,(0,int(ly)),(W,int(ly)),(0,140,255),2)
    s=480/W;v=cv2.resize(v,(480,int(H*s)))
    if OUT=='d.json' and fr%2==0: cv2.imwrite(f'f{fr//2:04d}.jpg',v,[cv2.IMWRITE_JPEG_QUALITY,52])
    F.append(dict(n=len(boxes),B=sum(e[0]=='B' for e in ev),A=sum(e[0]=='A' for e in ev),V=sum(1 for x in vals if x<=fr),U=len(seen)))
    fr+=1
    if fr>=int(sys.argv[3]): break
el=time.time()-t0
json.dump(dict(fps=fps,F=F,proc_fps=fr/el,frames=fr,ids=len(seen),ev=ev,grace=int(8*fps),tracks={k:len(v) for k,v in trail.items()}),open(OUT,'w'))
print(fr,'frames',round(fr/el,1),'fps',len(seen),'ids',sum(e[0]=='B' for e in ev),'B',sum(e[0]=='A' for e in ev),'A')
