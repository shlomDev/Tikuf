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
