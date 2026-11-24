# Tikuf - project brief for a coding agent (Claude Code, Codex, Copilot Chat)
Paste this whole file as the first message, with the repository open. It is self-contained.

## 1. Role
You are a senior engineer taking over a working proof of concept (PoC). Work autonomously in phases, run and test everything, commit after each phase, and report real measured numbers. Never fake results. Do not ask the founder questions: decide, write the decision in `docs/DECISIONS.md`, continue.

## 2. Product
On Israeli buses an inspector checks Rav-Kav validations. We want an automatic, privacy-preserving system: a camera above the door counts boardings anonymously, a validation source reports taps, and the system flags boardings with no tap and reports load and non-validation statistics per vehicle, line, stop and time. Output is aggregate or event-level (time, door, line, trip), never a person. Goal: a pilot with the Ministry of Transport / one operator.
Context: a similar system reportedly already exists on Israeli buses (door sensors cross-checked with validations). Position this as a complement and ask operators for their existing counts and validation feed first (see docs/TECH_RESEARCH.md).

## 3. Hard constraints
1. No face recognition, no biometrics, no identity. Detect only "person" boxes; track IDs are anonymous.
2. Never store images or video in production; frames live in memory only.
3. No per-person records, no enforcement or fine workflow.
4. Do not intercept validator hardware (no audio sniffing, no electrical tapping). Validation data comes from a software feed, a simulator, or a passive optical reader of the validator light (`src/validator_light.py`).
5. Be honest about accuracy; every number must say whether it is measured, simulated or assumed.

## 3b. Stack
Python 3.10+, CPU only, ONNX Runtime, OpenCV, NumPy, SciPy, pytest. Free permissive-license components only (YOLOX-nano, own ByteTrack-style tracker). Do NOT add Ultralytics YOLO (AGPL-3.0) unless a paid license is obtained. Low-resource mode (Termux/edge boxes) must keep working: onnxruntime + opencv-headless, frame stride, small input size.

## 4. Current state (all in this repo)
- `src/track.py`: YOLOX-nano person detection (input 416, COCO class 0), two-stage ByteTrack-style tracker (Hungarian assignment, constant-velocity prediction, ID after 3 hits, drop after 20 misses), door-line counting (bottom-center of box crosses a horizontal line; inward = boarding, outward = alighting), writes annotated frames and `d.json`.
- `src/build.py`: self-contained HTML tracking dashboard.
- `src/sim.py`: top-down bus ride simulator (14 passengers, front entry door, rear exit, validator pole), camera-noise model (missed and double-counted boardings), matching and flagging, 300-ride batch statistics, mp4 render.
- Matching logic (`flag`): taps at the validator are tied to the person standing there (confident). App taps have no position and match by time window (-2 s to +8 s). Connected groups where boardings outnumber taps become "k of n boardings had no tap" (ambiguous) instead of a guess. Lone unmatched boardings are confident flags.
- `src/validator_light.py`: HSV green-light reader on a tight ROI with hysteresis and a duration filter (0.25-1.8 s); synthetic evaluation.
- `src/evaluate.py`: real accuracy against hand counts from `clips.csv`.
- `tests/test_core.py`: 3 tests (exact count with perfect camera, clean precision, light reader).

- `src/reconcile.py`: per-stop boardings vs all payment records (rav-kav, app, qr, pass) with an uncertainty band from camera miss/double-count rates; `reliable` is false when the evasion signal is below the camera error. `src/track_stats.py` and `docs/VIDEO_TESTS.md`: ID-stability proxies on generated clips (many IDs live under 1 s). `docs/READINESS.md` lists pilot blockers.

## 5. Measured vs simulated
- Measured: 53 FPS on CPU on the public OpenCV `vtest.avi` clip (first 400 frames: 22 IDs, 9 inward and 11 outward crossings at a line at 55% height). Distant people are missed.
- Simulated (assumptions: 25% non-payers, 15% app taps, camera errors as stated): perfect camera = exact per-ride count; 3% missed + 3% double counted = 91% of confident flags right, 93% of evaders flagged or narrowed to a pair, 0.53 mean count error per ride; 8%/8% = 80%, 85%, 0.99.
- Light reader (synthetic): 98.2% of valid taps, 0 false detections per hour, 23 ms median timing error; strong glare: 68.1% caught, 275 false detections per hour.
- NOT measured: counting accuracy on real bus footage.

## 6. Known weaknesses (fix in this order)
1. Distant/small people missed: larger model (YOLOX-s/m), larger input (640), overhead camera so people are large in frame.
2. Tracker has no appearance model or Kalman filter: ID switches in crowds. Replace with the reference ByteTrack, then measure ID switches.
3. Single-point line crossing: add hysteresis and a door-zone polygon.
4. No ground truth: film 3+ real entrance clips, hand count, run `src/evaluate.py`. Report MAE, double-count and miss rates, ID switches, FPS per hardware.
5. Overhead view needs a model fine-tuned on overhead head images; collect and label in the pilot.
6. Camera noise rates in `sim.py` are assumed; replace with measured rates once item 4 is done.
7. No persistence/API yet: add SQLite event store, FastAPI endpoints (`/state`, `/windows`, `/events` aggregates only), a `ValidationSource` interface (simulator, CSV replay, optical reader, operator API stub with a written field spec), and a reconciler with configurable `grace_seconds`, `exempt_rate`, `camera_error_margin`.
8. Heat: boards like the Pi AI HAT+ are rated 0-50 C ambient; plan an enclosure or industrial-rated hardware for in-bus use.

## 7. Phases
0. Reproduce the baseline: `pip install -r requirements-dev.txt`, `sh scripts/setup.sh`, run track, sim, tests; report differences.
1. Weaknesses 1-3 and real accuracy (needs the founder's clips; until then use public footage and say so).
2. Module refactor: capture, detector, tracker, line counter, events, store, sources, reconciler, api, dashboard.
3. ValidationSource abstraction and SQLite/FastAPI layer.
4. Reconciler against section 5 scenarios, table-driven tests (late taps, no taps, negative gap, exempt rate, small windows).
5. Privacy hardening: a test that fails if any image file is written; docs/PRIVACY.md kept current.
6. Demo packaging: one command to a live dashboard from webcam or video file; README quick start verified from a fresh clone.
7. Pilot readiness: docs/PILOT_INTEGRATION.md with the exact data fields needed (timestamp, vehicle, line, validator/door ID, no passenger data), pilot scope, success metrics, camera install needs.

## 8. Definition of done
One command starts a live demo; dashboard shows boardings, taps, flags (confident vs ambiguous) with confidence; tests green; accuracy report has real measurements; no image or personal data stored (tested); swapping the simulator for a real feed means implementing one class.

## 9. Reporting
End each phase with: what works, measured numbers, what does not, exact commands, top 3 risks. Be blunt about failures.
