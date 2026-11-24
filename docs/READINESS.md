# Readiness: where the product really stands
| Level | Meaning | Status |
|---|---|---|
| Demo-ready | Runs, shows the idea, honest labels | YES |
| Pilot-ready | Can be put on 3-5 buses and measured | NOT YET: see blockers |
| Production | Trusted for decisions | NO |

## Done
Detector + tracker + line counting (CPU), ride simulator with ambiguity-aware no-tap flagging, optical validator-light reader (synthetic), per-stop reconciliation with an uncertainty band (`src/reconcile.py`), accuracy tool (`src/evaluate.py`), tests (5), dashboards, privacy rules, pilot letter, research with sources, video tests on generated clips.

## Blockers to pilot-ready (in order)
1. Real accuracy: film 3+ real entrance clips, hand count, run `src/evaluate.py`. Needed first because tracking fragments IDs on every clip tried (docs/VIDEO_TESTS.md).
2. Overhead camera view (the front-door cameras look down the aisle at an angle; one frame showed 5 of about 9 people detected). Fine-tune on overhead head images collected in the pilot.
3. Validation data: operator feed including app/QR/pass payments (confirm what exists; a similar door-sensor system reportedly already runs on Israeli buses). Fallback: optical reader, which needs a real validator display clip (card and sticker are lime green; the reader must use a tight display ROI and detect change).
4. Hardware for heat (0-50 C ambient rating on the Pi AI HAT+ vs a parked bus in summer).
5. Legal review (privacy law, enforcement use) and operator/Ministry consent for installation.

## Honest limits
Evasion rate low (e.g. 8%) means camera error (3% missed + 3% double) is as large as the signal: `src/reconcile.py` reports a band and flags `reliable: False`. Use for ranking trips/stops and sending inspectors, not for quoting absolute rates or fining people.
