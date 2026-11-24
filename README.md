# gap-counter

Proof of concept for public transport: count people boarding a bus anonymously (heads/people get a temporary numeric ID, no faces, no stored images) and compare against fare validations, to flag boardings with no tap and to produce load statistics. Aggregate and event-level output only.

## Status (read this first)
Demo-ready: yes. Pilot-ready: not yet (see `docs/READINESS.md`). Tracking fragments IDs on generated bus clips (`docs/VIDEO_TESTS.md`), so real-footage accuracy comes first.

| | |
|---|---|
| Works | Person detection (YOLOX-nano, ONNX, CPU), ByteTrack-style tracking, door-line counting, HTML dashboards, ride simulator, no-tap flagging, optical validator-light reader |
| Measured | ~53 FPS on CPU on a public pedestrian clip (400 frames). Light reader on synthetic footage: 98% of valid taps caught in normal conditions, 68% under strong glare |
| Simulated | Passengers, taps and camera errors in `sim.py` (assumed rates: 25% non-payers, 15% app taps, 3% camera errors) |
| NOT measured | Counting accuracy on a real bus. No hand-counted ground truth exists yet |
| Missing | A real validation feed. Real validator display footage |

Published research suggests overhead-camera counting reaches roughly 92-96% (see `docs/TECH_RESEARCH.md`). Do not quote any accuracy figure of ours until `src/evaluate.py` has run on real footage.

## Quick start
    python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
    pip install -r requirements-dev.txt
    sh scripts/setup.sh                                     # downloads m.onnx (model) and v.avi (sample clip)
    python src/track.py v.avi 0.55 400                      # video, line height (0-1), max frames
    python src/build.py                                     # writes gap-counter-demo.html
    python src/sim.py 3 && python src/build_sim_dashboard.py   # ride simulation + dashboard + bus-simulation.mp4
    python src/validator_light.py                           # optical validator reader, synthetic test
    python -m pytest -q tests

## Open in VS Code
1. File > Open Folder > this folder. Accept the recommended extensions.
2. Run and Debug (Ctrl+Shift+D) has 6 ready configurations (track, dashboards, simulation, validator test, evaluation).
3. Testing panel runs `tests/` with pytest. Open any generated `*.html` with Live Server.
4. To work with an AI coding agent (Claude Code, Codex, Copilot Chat), give it `docs/PROJECT_PROMPT.md`.

## Layout
    src/track.py               detect + track + count (video -> frames + d.json)
    src/build.py               tracking dashboard (self-contained HTML)
    src/sim.py                 bus ride simulator, matching and flagging logic, batch statistics
    src/build_sim_dashboard.py simulation dashboard
    src/validator_light.py     reads the green validation light from a tight camera crop
    src/evaluate.py            real accuracy against hand counts (clips.csv)
    src/reconcile.py           per-stop boardings vs all payment records, with camera-error band
    src/track_stats.py         ID-stability stats for clips without ground truth
    tests/                     pytest
    docs/                      PROJECT_PROMPT, READINESS, VIDEO_TESTS, TECH_RESEARCH, PRIVACY, PILOT_LETTER

## Dual-camera clips and bigger model
    python src/track.py clip.mp4 0.55 600 left out.json    # left|right|full, optional output json
    python src/track_stats.py out.json
    MODEL=ms.onnx python src/track.py ...                  # YOLOX-s (curl .../yolox_s.onnx), tunables: IOU1 MISS_S CONF MINH

## Measure real accuracy (do this first)
Film 3+ clips (20-60 s) of a real entrance, camera high and facing down at the door: 1 person, 5 people, a crowd. Count crossings by hand, copy `clips.example.csv` to `clips.csv`, fill it, run `python src/evaluate.py clips.csv`.

## Matching logic in one paragraph
Taps made at the validator are tied to the person standing there (confident). App taps have no position, so they are matched by time window. If several boardings compete for fewer taps, the system reports "k of n boardings had no tap" instead of guessing who (ambiguous group). With a perfect camera the count per ride is exact; camera mistakes are the remaining error.

## Important context
A similar system reportedly already runs on Israeli buses (door sensors cross-checked against validations, with an announcement when the gap is large; media report, unverified). Position this project as a complement, and ask operators for their existing counts and validation feed before installing hardware. Details in `docs/TECH_RESEARCH.md`.

## Privacy and legal
No face recognition, no biometrics, no stored images, aggregate output. Fining individuals from video needs legal review. See `docs/PRIVACY.md`. This repository is not legal advice.

## License
Not chosen yet. Dependencies: YOLOX (Apache-2.0, verify), ONNX Runtime, OpenCV, NumPy, SciPy. Do not add Ultralytics YOLO (AGPL-3.0) to a closed commercial product without a paid license.
