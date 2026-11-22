#!/bin/sh
# Downloads the free YOLOX-nano person model and a public pedestrian sample clip into the repo root.
set -e
curl -L -o m.onnx https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_nano.onnx
curl -L -o v.avi https://raw.githubusercontent.com/opencv/opencv/master/samples/data/vtest.avi
echo "done: m.onnx v.avi"
