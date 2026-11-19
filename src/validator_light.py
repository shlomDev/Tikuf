"""Reads the validator's green 'valid' light from a tight camera crop. Emits VALIDATION events (time only).
Privacy: only the ROI crop is analysed; the rest of the frame is discarded at once; nothing is stored."""
import cv2,numpy as np,random,sys
FPS=20;R2=150;BR=70
class LightReader:
    def __init__(s,on=.25,off=.10,min_on=.25,max_on=1.8):
        s.on,s.off,s.mn,s.mx=on,off,min_on,max_on;s.t_rise=None;s.out=[]
    def feed(s,roi,t):
        h=cv2.cvtColor(roi,cv2.COLOR_BGR2HSV);m=(h[...,0]>40)&(h[...,0]<85)&(h[...,1]>100)&(h[...,2]>100);f=m.mean()
        if s.t_rise is None and f>s.on: s.t_rise=t
        elif s.t_rise is not None and f<s.off:
            d=t-s.t_rise
            if s.mn<=d<=s.mx: s.out.append(s.t_rise)
            s.t_rise=None
def synth(seed,n=300,noise=8,glare=.15,hand=True):
    r=random.Random(seed);rng=np.random.default_rng(seed);ev=[];t=2.0
    for _ in range(n):
        t+=r.uniform(1.4,8);k=r.choices(['ok','reject','fake','green_obj'],[.7,.1,.15,.05])[0];ev.append((t,k,r.uniform(.6,1.2)))
    T=t+3;frames=int(T*FPS);return ev,T,frames
def frame(ev,i,noise,glare,rng,r):
    t=i/FPS;im=np.full((48,48,3),50,np.float32)*(1+.15*np.sin(t/7))
    for (te,k,d) in ev:
        if te<=t<te+d:
            if k=='ok': im[:]=(60,180,60)
            elif k=='reject': im[:]=(40,40,200)
            elif k=='green_obj': im[:]=(70,160,80)
        if k in('ok','reject','fake') and te-.4<=t<te: im[:14]*=.4
    if r.random()<glare:
        cy,cx=r.randrange(48),r.randrange(48);yy,xx=np.ogrid[:48,:48];im[(yy-cy)**2+(xx-cx)**2<R2]+=BR
    return np.clip(im+rng.normal(0,noise,im.shape),0,255).astype(np.uint8)
def evaluate(seed,noise,glare):
    ev,T,F=synth(seed);rng=np.random.default_rng(seed+1);r=random.Random(seed+2);lr=LightReader()
    # green_obj events last long: stretch them to model a green sleeve/bag held over the sensor (2-4 s)
    ev=[(te,k,(r.uniform(2.2,4) if k=='green_obj' else d)) for te,k,d in ev]
    for i in range(F): lr.feed(frame(ev,i,noise,glare,rng,r),i/FPS)
    truth=[te for te,k,d in ev if k=='ok'];used=set();tp=0;err=[]
    for te in truth:
        for j,x in enumerate(lr.out):
            if j not in used and abs(x-te)<.5: used.add(j);tp+=1;err.append(abs(x-te));break
    fp=len(lr.out)-tp;rej=sum(1 for te,k,d in ev if k=='reject' and any(abs(x-te)<.5 for x in lr.out))
    return tp,len(truth),fp,rej,sum(1 for e in ev if e[1]=='reject'),float(np.median(err)) if err else 0,T
if __name__=='__main__':
    for name,nz,gl in (('clean',3,0),('normal',8,.15),('harsh',20,.4)):
        a=np.array([evaluate(s,nz,gl) for s in range(3)],dtype=float).sum(0)
        print(f'{name}: valid taps caught {a[0]/a[1]:.1%} | false detections per hour {a[2]/(a[6]/3600):.1f} | rejected cards miscounted {a[3]/a[4]:.1%} | median timing error {np.median([evaluate(s,nz,gl)[5] for s in range(3)])*1000:.0f} ms')
