# Technology research (Nov 2026)
Sources are listed so each claim can be checked. Nothing here is a measurement of our own system.

## Camera placement and accuracy
- Overhead camera above each door looking down is the standard. Stereo/3D head detection is sold for buses (Hikvision on-board passenger counting).
- Depth-only LiDAR neural counting: correct count in about 96% of door openings on a train (NAPC, IEEE OJ-ITS 2022, doi 10.1109/OJITS.2021.3139393). Depth data does not allow identifying individuals.
- RGB-D head-detection counting: up to 92% on real bus video (arXiv 1804.04339, PCDS dataset).
- Plain RGB is more sensitive to lighting than depth (Springer IAS-14 chapter, RGB-D bus counting).
- Existing bus security cameras are normally wide-angle and not overhead: expect worse counts. Fine for a demo, not for fare-grade claims. (Our judgement, test on real footage.)

## Free software and licenses
- Detector used here: YOLOX-nano ONNX (Megvii YOLOX releases). Tracker: ByteTrack-style (own implementation). Verify each license before commercial use.
- Ultralytics YOLO11 is AGPL-3.0; closed commercial use needs a paid Enterprise License (Ultralytics repo and Hugging Face card). Not free for a company product.
- Overhead views need fine-tuning on overhead head images. Collect and label them during the pilot (CVAT is a free labeling tool). Check licenses of any public dataset.

## Hardware
- Raspberry Pi 5 + AI HAT+ with Hailo-8L: 13 TOPS, $70 (26 TOPS Hailo-8 version $110). Hailo is an Israeli company. Ambient rating 0-50 C: a parked bus in summer may exceed this, so use an enclosure or industrial-rated parts (inference, verify). Sources: SparkFun, Tom's Hardware, The Pi Hut, TechSpot.
- Raspberry Pi AI Camera (Sony IMX500, $70) runs the model inside the sensor, so only metadata leaves the camera.

## Validation data (two ways)
1. API / feed from the validator system: sees every validation. Needs the Ministry or an operator.
2. Optical reader of the validator light (`src/validator_light.py`): independent of data access but needs operator consent to mount, cannot see validations that do not light the box (for example remote app validations), and is sensitive to sunlight (68% caught under strong glare in our synthetic test).

## Existing system in Israel (verify)
ice.co.il, 27 May 2026, summarising a Kan 11 podcast interview with an unnamed technology VP: door sensors (volume/weight plus image-processing models) count boardings and alightings per stop, cross-check them in real time against validator and app validations, and play an announcement when the gap passes a threshold. Operator and fleet size not stated. Consequences: operators already hold counts and a validation feed; position this project as a complement (event-level flags, ambiguity handling, inspector dispatch), not as something new.
URL: https://www.ice.co.il/culture/news/article/1114438
