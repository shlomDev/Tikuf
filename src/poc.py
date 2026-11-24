"""Tikuf POC: one command, one honest answer.

    python src/poc.py --video v.avi --line 0.55 --frames 400 --payments payments.csv --out poc.html

Chain: count boardings from the video (real detector + tracker), read the taps that
were actually recorded, reconcile them per stop, and report the no-tap estimate as a
RANGE whose width is the camera's own error. If the signal is smaller than the error,
the report says so instead of quoting a rate.

Everything measurable is labelled measured; everything assumed is labelled assumed.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import math
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def band(count: int, miss: float, dup: float) -> int:
    """Half-width of the uncertainty band: camera error applied to the count."""
    return int(math.ceil(max(0.0, count) * (miss + dup)))


def trip_summary(boarded: int, paid: int, miss: float = 0.03, dup: float = 0.03) -> dict:
    """Trip-level no-tap estimate with its honest range."""
    board = max(0, int(boarded))
    taps = max(0, int(paid))
    unpaid = max(0, board - taps)
    half = band(board, miss, dup)
    low, high = max(0, unpaid - half), unpaid + half
    return {
        "boarded": board,
        "paid": taps,
        "unpaid_est": unpaid,
        "low": low,
        "high": high,
        "band": half,
        "reliable": low > 0,
        "rate": (unpaid / board) if board else 0.0,
        "verdict": (
            "signal exceeds camera error" if low > 0
            else "inside camera error: ranking only, do not quote a rate"
        ),
    }


def per_stop(boards: list[dict], payments: list[dict], miss: float, dup: float) -> list[dict]:
    """Same maths, one row per stop."""
    stops: dict[str, list[int]] = {}
    for b in boards:
        if str(b.get("type", "board")) == "board":
            key = str(b.get("stop", "?"))
            stops.setdefault(key, [0, 0])[0] += 1
    for p in payments:
        key = str(p.get("stop", "?"))
        stops.setdefault(key, [0, 0])[1] += 1
    rows = []
    for stop in sorted(stops, key=lambda k: (len(k), k)):
        b, p = stops[stop]
        rows.append({"stop": stop, **trip_summary(b, p, miss, dup)})
    return rows


def count_boardings(video: str, line: str, frames: str, model: str | None = None) -> dict:
    """Run the real tracker and return its counts. Frames are never written here."""
    out = Path(tempfile.mkdtemp(prefix="tikuf-")) / "d.json"
    # the tracker runs in a temp cwd, so every path handed to it must be absolute
    model_path = Path(model).resolve() if model else (HERE.parent / "m.onnx").resolve()
    if not model_path.exists():
        raise SystemExit(f"model not found: {model_path}\nrun: sh scripts/setup.sh")
    env = dict(os.environ, WRITE_FRAMES="0", SIM_TAPS="0", MODEL=str(model_path))
    video_path = Path(video).resolve()
    if not video_path.exists():
        raise SystemExit(f"video not found: {video_path}")
    cmd = [sys.executable, str(HERE / "track.py"), str(video_path), line, frames, "full", str(out)]
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=str(out.parent))
    if proc.returncode != 0:
        raise SystemExit(f"tracking failed (exit {proc.returncode})\n{proc.stderr.strip()[-800:]}")
    d = json.loads(out.read_text())
    ids_in = {e[2] for e in d["ev"] if e[0] == "B"}
    ids_out = {e[2] for e in d["ev"] if e[0] == "A"}
    return {
        "boarded": len(ids_in),
        "exited": len(ids_out),
        "frames": d["frames"],
        "proc_fps": d.get("proc_fps", 0.0),
        "ids": d.get("ids", 0),
    }


def sim_evidence(rides: int = 100) -> dict:
    """Simulated rides have ground truth, so accuracy can be stated instead of assumed."""
    import sim
    stats = sim.batch(0.03, 0.03, n=rides)
    A = sim.make(0)
    events, _ = sim.run(A)
    B, V, _ = sim.perceive(events, 0, 0.03, 0.03)
    confident, groups = sim.flag(B, V)
    return {
        "rides": rides,
        "recall": stats["recall"],
        "precision": stats["precision"],
        "mae": stats["mae"],
        "bias": stats["bias"],
        "example_passengers": len(A),
        "example_evaders": sum(1 for a in A if not a["pays"]),
        "example_confident": len(confident),
        "example_groups": len(groups),
        "example_group_people": sum(g[2] for g in groups),
    }


def read_payments(path: str | None) -> list[dict]:
    if not path:
        return []
    with open(path, newline="") as fh:
        return [row for row in csv.DictReader(fh)]


def report_html(tracking: dict, trip: dict, rows: list[dict], args, sim: dict | None = None) -> str:
    def money(v): return f"{v:,.0f}"

    stop_rows = "".join(
        f"<tr><td>{html.escape(r['stop'])}</td><td>{r['boarded']}</td><td>{r['paid']}</td>"
        f"<td>{r['unpaid_est']}</td><td>{r['low']}–{r['high']}</td>"
        f"<td class={'ok' if r['reliable'] else 'warn'}>{'signal' if r['reliable'] else 'inside error'}</td></tr>"
        for r in rows
    ) or "<tr><td colspan=6 class=mut>no per-stop data (single-stop run)</td></tr>"

    sim = sim or sim_evidence()
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Tikuf POC report</title>
<style>
:root{{--bg:#0f1413;--s:#171f1d;--ink:#e8f1ee;--mut:#8fa3a0;--t:#3fc8bf;--warn:#e0a33a;--bad:#e06c60;--ok:#54c98a;--ln:#26302e}}
body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 ui-sans-serif,system-ui,"IBM Plex Sans",sans-serif}}
main{{max-width:820px;margin:0 auto;padding:26px 18px 60px}}
h1{{font-size:22px;margin:0 0 2px}} .sub{{color:var(--mut);font-size:13px;margin-bottom:22px}}
.cards{{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:20px}}
@media(min-width:620px){{.cards{{grid-template-columns:repeat(4,1fr)}}}}
.c{{background:var(--s);border:1px solid var(--ln);border-radius:12px;padding:12px 14px}}
.c b{{display:block;font-size:26px;font-variant-numeric:tabular-nums;line-height:1.15}}
.c span{{color:var(--mut);font-size:12px;text-transform:uppercase;letter-spacing:.06em}}
.c.hi b{{color:var(--t)}}
.verdict{{border-radius:12px;padding:14px 16px;margin-bottom:20px;font-weight:600}}
.verdict.good{{background:rgba(84,201,138,.12);border:1px solid var(--ok);color:var(--ok)}}
.verdict.mid{{background:rgba(224,163,58,.12);border:1px solid var(--warn);color:var(--warn)}}
table{{width:100%;border-collapse:collapse;background:var(--s);border:1px solid var(--ln);border-radius:12px;overflow:hidden;margin-bottom:20px}}
th{{text-align:left;font-size:11px;letter-spacing:.07em;text-transform:uppercase;color:var(--mut);padding:9px 10px;border-bottom:1px solid var(--ln)}}
td{{padding:9px 10px;border-bottom:1px solid #1d2624;font-variant-numeric:tabular-nums}} tr:last-child td{{border:0}}
.ok{{color:var(--ok)}} .warn{{color:var(--warn)}} .mut{{color:var(--mut)}}
.note{{background:var(--s);border:1px solid var(--ln);border-radius:12px;padding:14px 16px;color:var(--mut);font-size:13.5px}}
.note b{{color:var(--ink)}}
</style></head><body><main>
<h1>Tikuf POC report</h1>
<div class="sub">{html.escape(str(args.video))} &middot; line {html.escape(str(args.line))} &middot; {tracking['frames']} frames at {tracking['proc_fps']:.1f} FPS on CPU</div>

<div class="cards">
  <div class="c"><span>boardings counted</span><b>{trip['boarded']}</b></div>
  <div class="c"><span>taps recorded</span><b>{trip['paid']}</b></div>
  <div class="c hi"><span>no-tap estimate</span><b>{trip['unpaid_est']}</b></div>
  <div class="c"><span>honest range</span><b>{trip['low']}–{trip['high']}</b></div>
</div>

<div class="verdict {'good' if trip['reliable'] else 'mid'}">
{'Signal is larger than the camera error: worth acting on.' if trip['reliable'] else 'Signal sits inside the camera error band. Use it to rank stops, never as a rate.'}
</div>

<table>
<thead><tr><th>Stop</th><th>Boarded</th><th>Paid</th><th>No-tap est.</th><th>Range</th><th>Read</th></tr></thead>
<tbody>{stop_rows}</tbody>
</table>

<h2 style="font-size:15px;margin:22px 0 8px">Simulation with known ground truth</h2>
<table>
<thead><tr><th>Metric</th><th>Value</th><th>Meaning</th></tr></thead>
<tbody>
<tr><td>No-tap recall</td><td>{sim['recall']:.0%}</td><td>share of real evaders the system flags</td></tr>
<tr><td>Precision</td><td>{sim['precision']:.0%}</td><td>share of flags that are real evaders</td></tr>
<tr><td>Count error</td><td>{sim['mae']:.2f} people/ride</td><td>average miss in the boarding count</td></tr>
<tr><td>Bias</td><td>{sim['bias']:+.2f} people/ride</td><td>negative means it under-reports, never accuses</td></tr>
<tr><td>Example ride</td><td>{sim['example_passengers']} boarded, {sim['example_evaders']} unpaid</td><td>flagged {sim['example_confident']} with confidence + {sim['example_group_people']} in {sim['example_groups']} ambiguous group(s)</td></tr>
</tbody></table>
<div class="sub" style="margin-top:-8px">Simulated: {sim['rides']} rides, assumed 3% missed + 3% double-counted, 25% non-payers. This is the only section with ground truth.</div>

<div class="note">
<b>Measured:</b> {tracking['boarded']} boardings and {tracking['exited']} exits from real detection and tracking on this clip, {tracking['ids']} anonymous IDs.<br>
<b>Assumed:</b> camera error {args.miss:.0%} missed + {args.dup:.0%} double-counted. Change it with --miss and --dup; every number above moves with it.<br>
<b>Not measured:</b> counting accuracy, because this clip has no hand-counted ground truth. Run <code>python src/evaluate.py clips.csv</code> on real footage before quoting any accuracy.
</div>
</main></body></html>"""


def main() -> None:
    ap = argparse.ArgumentParser(description="Tikuf POC: boardings vs taps, with an honest band")
    ap.add_argument("--video", required=True, help="clip of the door")
    ap.add_argument("--line", default="0.55", help="door line height, 0-1")
    ap.add_argument("--frames", default="400", help="max frames to process")
    ap.add_argument("--payments", help="CSV of payment records: stop,method")
    ap.add_argument("--taps", type=int, help="total taps, if there is no payments CSV")
    ap.add_argument("--miss", type=float, default=0.03, help="assumed missed detections")
    ap.add_argument("--dup", type=float, default=0.03, help="assumed double counts")
    ap.add_argument("--model", help="ONNX model path (default m.onnx)")
    ap.add_argument("--out", default="poc.html", help="HTML report path")
    ap.add_argument("--no-sim", action="store_true", help="skip the simulated-rides section")
    args = ap.parse_args()

    tracking = count_boardings(args.video, args.line, args.frames, args.model)
    payments = read_payments(args.payments)
    paid = args.taps if args.taps is not None else len(payments)
    trip = trip_summary(tracking["boarded"], paid, args.miss, args.dup)
    rows = per_stop([{"stop": "TRIP", "type": "board"}] * tracking["boarded"], payments,
                    args.miss, args.dup) if payments else []
    Path(args.out).write_text(report_html(tracking, trip, rows, args, None if args.no_sim else sim_evidence()), encoding="utf-8")
    print(f"boarded {trip['boarded']} | taps {trip['paid']} | no-tap {trip['unpaid_est']} "
          f"range {trip['low']}-{trip['high']} | {trip['verdict']}")
    print(f"report: {args.out}")


if __name__ == "__main__":
    main()
