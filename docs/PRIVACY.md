# Privacy principles (design rules)
1. Detect only "person" boxes. No face recognition, no embeddings, no biometric data, no identity.
2. Track IDs are anonymous integers, valid only within one door-opening or session. Never linked to a card, phone or person.
3. Frames are processed in memory and discarded. No images or video are stored in production. (Demo frames in this repo come from a public sample clip and synthetic drawings.)
4. Output is counts, timestamps and event flags (time, door, line, trip). No per-person records.
5. A flag is an event, not an accusation. Its purpose is to direct inspectors and produce statistics. Fining a person from video needs legal review first.
6. Processing runs on the device. Only metadata leaves the vehicle.
7. Validator reader: analyse only a tight crop of the validator light. A plain light sensor gives the same signal with no image at all and is preferred.
8. Before any real installation: legal review under Israeli privacy law, operator and Ministry approval, and a written data-retention rule. This document is not legal advice.
