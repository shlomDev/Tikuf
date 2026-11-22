import sys,os;sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..','src'))
import sim,validator_light as vl
def test_perfect_camera_count_is_exact():
    for s in range(40):
        A=sim.make(s);ev,_=sim.run(A);B,V,_=sim.perceive(ev,s,0,0);C,G=sim.flag(B,V)
        assert len(C)+sum(g[2] for g in G)==sum(1 for a in A if not a['pays'])
def test_batch_clean_precision():
    r=sim.batch(0,0,n=60);assert r['precision']>0.95 and r['mae']<0.2
def test_light_reader_normal_conditions():
    tp,n,fp,rej,nrej,_,T=vl.evaluate(0,8,.15);assert tp/n>0.9 and fp<=2 and rej==0
