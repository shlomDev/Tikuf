# gap-counter

Proof of concept: count people boarding a bus with a camera (anonymous tracking IDs, no faces, no stored images) and compare against fare validations to estimate the validation gap per vehicle, line and time window. Aggregate statistics only.

## Status
- Works: YOLOX-nano person detection (ONNX, CPU), ByteTrack-style tracking, virtual-line counting, HTML dashboard.
- Measured: ~53 FPS on CPU on a sample pedestrian clip (400 frames, 22 IDs).
- NOT measured: counting accuracy (no hand-counted ground truth yet).
- Simulated: validations (70% of crossings, 1-10 s delay). No real Rav-Kav feed.

## Run
    pip install -r requirements.txt
    curl -L -o m.onnx https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_nano.onnx
    curl -L -o v.avi https://raw.githubusercontent.com/opencv/opencv/master/samples/data/vtest.avi
    python src/track.py v.avi 0.55 400   # video, line height fraction, max frames
    python src/build.py                  # writes the dashboard HTML

## Next
1. Hand-count 3+ real entrance clips and measure accuracy.
2. Replace tracker with real ByteTrack; larger model for small/distant people.
3. ValidationSource interface + SQLite + FastAPI + reconciler.
4. Pilot: data request to operator / national authority.

Privacy: no face recognition, no image storage, aggregate output only.
