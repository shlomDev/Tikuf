import csv,json,subprocess,sys,os
# clips.csv columns: video,line_y,max_frames,true_in,true_out   (true_* = hand-counted people crossing the door line)
rows=list(csv.DictReader(open(sys.argv[1])));T=E=0;res=[]
for r in rows:
    subprocess.run([sys.executable,os.path.join(os.path.dirname(os.path.abspath(__file__)),'track.py'),r['video'],r['line_y'],r['max_frames']],check=True,capture_output=True);d=json.load(open('d.json'))
    bi=sum(e[0]=='B' for e in d['ev']);ao=sum(e[0]=='A' for e in d['ev']);ti,to=int(r['true_in']),int(r['true_out'])
    res.append((r['video'],ti,bi,to,ao));T+=ti+to;E+=abs(bi-ti)+abs(ao-to)
print('clip | true_in sys_in | true_out sys_out')
for x in res: print(*x,sep=' | ')
print(f'total true crossings {T}, total absolute error {E}, error rate {E/max(T,1):.1%}')
