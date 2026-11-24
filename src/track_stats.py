"""Tracking-stability stats for clips with no ground truth: how many IDs, how long they live, how fragmented they are.
Usage: python src/track_stats.py out1.json out2.json ...   (files written by track.py with an output name)"""
import json,sys,numpy as np
for f in sys.argv[1:]:
    d=json.load(open(f));fps=d['fps'];L=np.array(list(d['tracks'].values()))/fps;n=np.array([x['n'] for x in d['F']])
    print(f"{f}: {d['frames']} frames, people/frame mean {n.mean():.1f} max {n.max()}, IDs {len(L)}, median ID life {np.median(L):.1f}s, IDs under 1s {np.mean(L<1):.0%}, longest {L.max():.1f}s")
