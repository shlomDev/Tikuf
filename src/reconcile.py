"""Per-stop reconciliation of camera boardings against ALL payment records (rav-kav, app, qr, pass...).
Counts are compared, never individuals. Camera error is turned into an uncertainty band, so the report says
when an evasion signal is smaller than the camera's own error (then it is only good for ranking, not for quoting a rate).
CSV usage: python src/reconcile.py boards.csv payments.csv [miss] [dup]   (boards: stop,type ; payments: stop,method)"""
import csv,sys,math
from collections import defaultdict
def reconcile(boards,payments,miss=0.03,dup=0.03):
    b=defaultdict(int);p=defaultdict(int);m=defaultdict(lambda:defaultdict(int))
    for e in boards:
        if e['type']=='board': b[e['stop']]+=1
    for x in payments: p[x['stop']]+=1;m[x['stop']][x.get('method','?')]+=1
    rep={}
    for s in sorted(set(b)|set(p),key=str):
        band=math.ceil(b[s]*(miss+dup));u=max(0,b[s]-p[s])
        rep[s]=dict(boarded=b[s],paid=p[s],methods=dict(m[s]),unpaid_est=u,low=max(0,u-band),high=u+band,reliable=max(0,u-band)>0)
    B=sum(b.values());P=sum(p.values());band=math.ceil(B*(miss+dup));u=max(0,B-P)
    rep['TRIP']=dict(boarded=B,paid=P,unpaid_est=u,low=max(0,u-band),high=u+band,reliable=max(0,u-band)>0)
    return rep
if __name__=='__main__':
    bo=list(csv.DictReader(open(sys.argv[1])));pa=list(csv.DictReader(open(sys.argv[2])))
    mi=float(sys.argv[3]) if len(sys.argv)>3 else .03;du=float(sys.argv[4]) if len(sys.argv)>4 else .03
    for k,v in reconcile(bo,pa,mi,du).items(): print(k,v)
