"""Tracker helpers that need no video, so they can be unit tested.

Fragmentation is the product's real blocker: on a real boarding clip 50% of IDs
lived under a second, so one person could be counted twice. The cause is the IoU
gate alone - when a detection jitters or a person is partly hidden, the box stops
overlapping its prediction and the person is re-issued a new ID. A second-chance
match on centre distance recovers those, which is what `match_by_distance` does.
"""
from __future__ import annotations

import math


def centre(box):
    return ((box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0)


def match_by_distance(tracks, dets, max_ratio: float = 1.0):
    """Greedy nearest-centre matching. Distance is normalised by box height, so a
    tall person in the foreground is allowed the same relative movement as a small
    one far away. Returns [(track_index, det_index)] with one det per track."""
    cand = []
    for i, t in enumerate(tracks):
        tb = t.pred() if hasattr(t, "pred") else t
        tx, ty = centre(tb)
        th = max(1.0, tb[3] - tb[1])
        for j, d in enumerate(dets):
            dx, dy = centre(d)
            dh = max(1.0, d[3] - d[1])
            dist = math.hypot(dx - tx, dy - ty) / max(1.0, (th + dh) / 2.0)
            if dist < max_ratio:
                cand.append((dist, i, j))
    cand.sort()
    used_t, used_d, pairs = set(), set(), []
    for _, i, j in cand:
        if i in used_t or j in used_d:
            continue
        used_t.add(i)
        used_d.add(j)
        pairs.append((i, j))
    return pairs
