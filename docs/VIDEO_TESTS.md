# Video tests on generated bus clips (Nov 2026)
Footage: the 4 photoreal drafts from the supplied package (`Bus-CCTV-Continuation`, `Bus-CCTV-Motion-Test`, `Israeli-Bus-Photoreal-Video`, `Israeli-Bus-Crowd-Video`). The 5 cartoon-style 3D renders were not used (a real-person detector does not apply to them). Dual-camera clips are analysed per half (`track.py ... left|right`).
IMPORTANT: these clips are generated, have no hand-counted ground truth and may contain inconsistent people between frames. Results below are stability proxies, not accuracy.

## Proxy metrics (YOLOX-nano, defaults before tuning)
| Clip / view | People per frame (mean, max) | IDs assigned | Median ID life | IDs under 1 s |
|---|---|---|---|---|
| CCTV-Continuation left | 4.8, 7 | 25 | 0.8 s | 56% |
| CCTV-Continuation right | 4.9, 9 | 17 | 1.8 s | 18% |
| CCTV-Motion-Test left / right | 4.5, 6 / 6.8, 8 | 10 / 9 | 1.2 s / 3.4 s | 50% / 22% |
| Photoreal left / right | 4.8, 7 / 6.2, 9 | 9 / 12 | 1.3 s / 2.0 s | 22% / 42% |
| Crowd (full frame, 21.5 s) | 9.4, 13 | 56 | 2.0 s | 27% |

## Tuning (3 clips)
Lower IoU gate (0.25 -> 0.15) and longer track memory (2 s) give a small gain (e.g. 25 -> 22, 56 -> 51 IDs); now the defaults (env IOU1, MISS_S, CONF, MINH). A larger detector (YOLOX-s, `MODEL=ms.onnx`) finds more people (peak 8/8/16 vs 7/9/13) and lowers fragmentation on two clips (56%->33%, 18%->8%), not on the crowd clip (24%), at several times the compute.

## Reading
Tracks are still fragmented: many IDs live under 1 s while only ~5-13 people are visible. If this holds on real footage, counting by unique ID will over-count, and boardings must be counted by line crossing with a per-track one-time rule plus a re-entry guard. Do not tune further on generated clips; film real entrances, hand count, and run `src/evaluate.py`.

Reproduce: `python src/track.py <clip> 0.55 600 left out.json` then `python src/track_stats.py out.json`.


## Real footage (Nov 2026, free Wikimedia Commons clips)
Downloaded bus footage with no hand-counted ground truth either, so the same rule applies: these are stability proxies, not accuracy. Two clips mattered:

| Clip | View | IDs | Median ID life | IDs under 1 s |
|---|---|---|---|---|
| A man boarding a moving bus (720p, 182 frames) | door, handheld | 7 -> 6 | 1.2 s -> 1.5 s | 43% -> 33% |
| New Flyer XN40 interior (720p, 300 frames) | aisle, static | 13 -> 9 | 0.9 s -> 2.7 s | 54% -> 33% |

Left of the arrow is the old IoU-only matching; right is with the centre-distance second chance (`DIST1`, default 0.6). On the interior clip that is 31% fewer IDs and a 3x longer median track, which is the fragmentation the Readiness doc calls the blocker. Two clips showed zero people per frame (a night bus stop, a dark aisle) and one 320x240 clip would not decode: not every clip is usable, and that is worth knowing before filming.

Crossings are sensitive to line height on real footage: the same boarding clip gives 0, 1 or 2 boardings at line 0.50, 0.60, 0.70. A single visible person producing 2 crossings at 0.70 is a calibration error, not a tracking error, and it is the reason line height must be set per camera before any count is trusted.
