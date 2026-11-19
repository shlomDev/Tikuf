import cv2,numpy as np,random,json,base64,math,sys
DT=0.1;T=80;GR=8.0;LY=300;DI=(85,135);DO=(455,505);VAL=(140,290);EVERY=2
SEATS=[(x,y) for y in (110,160,210) for x in (220,280,340,400,460,520)]
def make(seed,N=14,ev=.25,late=.15):
    r=random.Random(seed);ts=sorted(r.uniform(3,38) for _ in range(N));st=r.sample(SEATS,N);A=[]
    for i,t in enumerate(ts):
        p=r.random()>ev;l=p and r.random()<late
        rt=[(110,300),(110,288)]+([VAL] if p and not l else [])+[st[i]]
        A.append(dict(id=i+1,t0=t,pays=p,late=l,route=rt,i=0,ph=0,w=0.,x=110.,y=345.,sp=r.uniform(45,65),te=min(76,t+r.uniform(18,42)),ld=r.uniform(3,6)))
    return A
def run(A):
    ev=[];pos=[]
    for k in range(int(T/DT)):
        t=k*DT;row=[]
        for a in A:
            if t<a['t0']: continue
            if a['w']>0: a['w']-=DT
            else:
                if a['i']>=len(a['route']):
                    if a['ph']==0 and t>=a['te']: a['route']=[(480,272),(480,350)];a['i']=0;a['ph']=1
                if a['i']<len(a['route']):
                    tx,ty=a['route'][a['i']];dx,dy=tx-a['x'],ty-a['y'];d=math.hypot(dx,dy);mv=a['sp']*DT;py=a['y']
                    if d<=mv:
                        a['x'],a['y']=tx,ty;a['i']+=1
                        if (tx,ty)==VAL and a['ph']==0: a['w']=1.2;ev.append((t+0.6,'V',a['id'],1))
                    else: a['x']+=dx/d*mv;a['y']+=dy/d*mv
                    if a['ph']==0 and py>LY>=a['y'] and DI[0]<=a['x']<=DI[1]:
                        ev.append((t,'B',a['id'],0))
                        if a['late']: ev.append((t+a['ld'],'V',a['id'],0))
                    if a['ph']==1 and py<=LY<a['y'] and DO[0]<=a['x']<=DO[1]: ev.append((t,'A',a['id'],0))
            if a['ph']==1 and a['y']>345: continue
            row.append((a['id'],a['x'],a['y']))
        pos.append(row)
    return sorted(ev),pos
def perceive(ev,seed,pm,pd):
    r=random.Random(seed+1000);B=[];V=[e for e in ev if e[1]=='V'];A=[e for e in ev if e[1]=='A']
    for e in ev:
        if e[1]!='B': continue
        if r.random()<pm: continue
        B.append((e[0],e[2],0))
        if r.random()<pd: B.append((e[0]+r.uniform(.5,2),e[2],1))
    return sorted(B),V,A
def flag(B,V):
    m=set();vu=set()
    for j,v in enumerate(V):
        if v[3]:
            for i,b in enumerate(B):
                if b[1]==v[2] and not b[2] and i not in m: m.add(i);vu.add(j);break
    for j,v in enumerate(V):
        if j in vu: continue
        for i,b in enumerate(B):
            if i not in m and b[0]-2<=v[0]<=b[0]+GR: m.add(i);break
    return [(b[0]+GR,b[1],b[2]) for i,b in enumerate(B) if i not in m]
def score(A,F):
    evd={a['id'] for a in A if not a['pays']};hit={f[1] for f in F if f[1] in evd}
    return len(hit),len(evd),len(hit),len(F)
def batch(pm,pd,n=300):
    h=e=tp=f=0;ex=[]
    for s in range(n):
        A=make(s);ev,_=run(A);B,V,_=perceive(ev,s,pm,pd);F=flag(B,V);a,b,c,d=score(A,F);h+=a;e+=b;tp+=c;f+=d;ex.append(d-b)
    return dict(recall=h/e,precision=tp/f,bias=sum(ex)/n,n=n)
def draw(A,t,row,B,V,F,k):
    im=np.full((360,640,3),(88,84,80),np.uint8);cv2.rectangle(im,(40,60),(600,300),(236,238,238),-1)
    for s in SEATS: cv2.rectangle(im,(s[0]-14,s[1]-12),(s[0]+14,s[1]+12),(210,214,214),-1)
    cv2.line(im,(DI[0],LY),(DI[1],LY),(0,170,255),3);cv2.line(im,(DO[0],LY),(DO[1],LY),(0,170,255),3)
    cv2.putText(im,'ENTRY',(DI[0]-4,322),0,.45,(255,255,255),1);cv2.putText(im,'EXIT',(DO[0]+5,322),0,.45,(255,255,255),1)
    tv=[v[0] for v in V if 0<=t-v[0]<.6];c=(200,140,0)
    cv2.rectangle(im,(VAL[0]+8,VAL[1]-26),(VAL[0]+22,VAL[1]-12),(0,200,0) if tv else c,-1);cv2.putText(im,'RAV-KAV',(VAL[0]-4,VAL[1]-32),0,.35,(60,60,60),1)
    tp={v[2] for v in V if 0<=t-v[0]<1.6};fl={f[1] for f in F if f[0]<=t}
    for i,x,y in row:
        p=(int(x),int(y));col=(140,140,140)
        if i in fl: col=(60,60,220)
        cv2.circle(im,p,9,col,-1)
        if i in tp: cv2.circle(im,p,13,(60,190,60),2)
        cv2.putText(im,str(i),(p[0]-5,p[1]+4),0,.38,(255,255,255),1)
    cv2.putText(im,f't={t:4.1f}s',(10,24),0,.6,(255,255,255),2)
    return im
if __name__=='__main__':
    S=int(sys.argv[1]);pm=pd=.03;A=make(S);ev,pos=run(A);B,V,Al=perceive(ev,S,pm,pd);F=flag(B,V)
    print('evaders',[a['id'] for a in A if not a['pays']],'late',[a['id'] for a in A if a['late']],'flags',[(round(f[0],1),f[1],f[2]) for f in F],'B',len(B),'V',len(V))
    vw=cv2.VideoWriter('/mnt/user-data/outputs/bus-simulation.mp4',cv2.VideoWriter_fourcc(*'mp4v'),10,(640,360));fr=[];ct=[]
    for k in range(len(pos)):
        t=k*DT;im=draw(A,t,pos[k],B,V,F,k);vw.write(im)
        if k%EVERY==0:
            cv2.imwrite('x.jpg',im,[cv2.IMWRITE_JPEG_QUALITY,50]);fr.append('data:image/jpeg;base64,'+base64.b64encode(open('x.jpg','rb').read()).decode())
            ct.append(dict(B=sum(b[0]<=t for b in B),A=sum(a[0]<=t for a in Al),V=sum(v[0]<=t for v in V),F=sum(f[0]<=t for f in F)))
    vw.release()
    lg=[dict(t=round(f[0],1),id=f[1],d=f[2]) for f in F];evd=[a['id'] for a in A if not a['pays']]
    R=dict(seed=S,ct=ct,log=lg,ev=evd,late=[a['id'] for a in A if a['late']],N=len(A),res=batch(pm,pd),clean=batch(0,0),rough=batch(.08,.08),every=EVERY*DT)
    json.dump(R,open('r.json','w'));json.dump(fr,open('fr.json','w'));print(R['res'],R['clean'],R['rough'],len(fr))
    cv2.imwrite('prev.jpg',draw(A,45,pos[450],B,V,F,450))
