#!/usr/bin/env python3
"""
round_log — turn a round's stats into your single biggest strokes leak.

Reads a handful of round-level stats (score, putts, fairways, greens,
up-and-downs, penalties), compares them to a baseline for your level, and
estimates which part of your game is bleeding the most strokes — then points
you at the practice focus that fixes it and hands it to practice_log.

This is a transparent *approximation* of strokes-gained, not tour-grade SG
(true SG needs shot-by-shot data). It finds your biggest leak *relative to a
typical player of your own level* from stats you can jot down after a round —
or that Claude reads straight off a photo of your scorecard. Zero dependencies.

Usage:
    python round_log.py add --level mid --score 89 --putts 34 \
        --fir 6/14 --gir 7 --updowns 3/11 --penalties 2 --notes "windy"
    python round_log.py show
"""

import argparse
import json
import os
import sys
from datetime import date

LOG_PATH = os.environ.get("RANGEY_ROUNDS", "round_log.json")

# Rough, defensible amateur benchmarks. Targets are "typical for this level",
# so the read finds your weak spot *relative to your own level* — not vs a pro.
BASELINES = {
    "beginner": {"putts": 37, "fir": 0.30, "gir": 0.15, "scramble": 0.20},
    "mid":      {"putts": 34, "fir": 0.45, "gir": 0.30, "scramble": 0.33},
    "low":      {"putts": 31, "fir": 0.55, "gir": 0.50, "scramble": 0.45},
    "scratch":  {"putts": 30, "fir": 0.62, "gir": 0.62, "scramble": 0.55},
}

# How much each missed unit roughly costs, in strokes. Deliberately simple.
W_FIR = 0.30       # per fairway missed below baseline
W_GIR = 0.55       # per green missed below baseline
W_SCRAMBLE = 0.80  # per failed up-and-down below baseline
W_PENALTY = 1.0    # per penalty stroke

# Map a leak category to the practice_log focus that fixes it.
FOCUS = {
    "Putting": "putting",
    "Approach": "approach",
    "Off the tee": "driver",
    "Short game": "short game",
}


def load():
    if not os.path.exists(LOG_PATH):
        return []
    try:
        with open(LOG_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        print(f"⚠  Could not read {LOG_PATH}; starting fresh.", file=sys.stderr)
        return []


def save(rounds):
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(rounds, f, indent=2, ensure_ascii=False)


def parse_ratio(s, default_denom=None):
    """'6/14' -> (6, 14); '6' -> (6, default_denom)."""
    if s is None:
        return (None, None)
    s = str(s)
    if "/" in s:
        a, b = s.split("/", 1)
        return (int(a), int(b))
    return (int(s), default_denom)


def analyze(r):
    """Return {category: {'lost': strokes, 'detail': str}} for a round dict."""
    b = BASELINES[r["level"]]
    cats = {}

    putts = r.get("putts")
    if putts is not None:
        cats["Putting"] = {
            "lost": max(0.0, putts - b["putts"]),
            "detail": f"{putts} putts vs ~{b['putts']} for your level",
        }

    gir = r.get("gir_made")
    if gir is not None:
        gir_pct = gir / 18
        gap = max(0.0, b["gir"] - gir_pct)
        cats["Approach"] = {
            "lost": gap * 18 * W_GIR,
            "detail": f"{gir}/18 greens ({gir_pct*100:.0f}%) vs ~{b['gir']*100:.0f}%",
        }

    fir_made = r.get("fir_made")
    penalties = r.get("penalties", 0)
    if fir_made is not None or penalties:
        lost = penalties * W_PENALTY
        bits = []
        if fir_made is not None:
            holes = r.get("fir_holes", 14)
            fir_pct = fir_made / holes
            lost += max(0.0, b["fir"] - fir_pct) * holes * W_FIR
            bits.append(f"{fir_made}/{holes} fairways ({fir_pct*100:.0f}%) vs ~{b['fir']*100:.0f}%")
        if penalties:
            bits.append(f"{penalties} penalt{'y' if penalties == 1 else 'ies'}")
        cats["Off the tee"] = {"lost": lost, "detail": ", ".join(bits)}

    ud_made = r.get("ud_made")
    ud_opp = r.get("ud_opp")
    if ud_opp is None and gir is not None:
        ud_opp = 18 - gir
    if ud_made is not None and ud_opp:
        scr = ud_made / ud_opp
        gap = max(0.0, b["scramble"] - scr)
        cats["Short game"] = {
            "lost": gap * ud_opp * W_SCRAMBLE,
            "detail": f"{ud_made}/{ud_opp} up-and-downs ({scr*100:.0f}%) vs ~{b['scramble']*100:.0f}%",
        }

    return cats


def print_breakdown(r):
    cats = analyze(r)
    if not cats:
        print("Not enough stats to analyze — add at least --putts and --gir.")
        return None

    ranked = sorted(cats.items(), key=lambda kv: kv[1]["lost"], reverse=True)
    total = sum(c["lost"] for _, c in ranked)
    score = r.get("score")

    head = f"⛳  WHERE YOUR STROKES GO   ({r['level']} baseline"
    head += f", round of {score})" if score is not None else ")"
    print("\n" + head)
    peak = max((c["lost"] for _, c in ranked), default=0) or 1.0
    for name, c in ranked:
        bars = "█" * int(round(c["lost"] / peak * 18))
        print(f"   {name:<12} {c['lost']:4.1f}  {bars}")
        print(f"   {'':<12}       └ {c['detail']}")

    leak, top = ranked[0]
    if total < 0.5:
        print("\n✅  Solidly balanced for your level — nothing is really bleeding.")
        print(f"    Marginal weak spot: {leak}.")
    else:
        print(f"\n🎯  Biggest leak: {leak}  (~{top['lost']:.1f} strokes vs your level)")

    focus = FOCUS[leak]
    print(f"\n→  Practice this: ask Claude \"build me a {focus} session\".")
    print(f"   Then log the pressure test:")
    print(f"   python practice_log.py add --focus \"{focus}\" --score <n>")
    print("\n(Estimate from round-level stats, not shot-by-shot strokes-gained — "
          "built to find your biggest leak, not for tour-grade precision.)")
    return leak


def cmd_add(args):
    fir_made, fir_holes = parse_ratio(args.fir, default_denom=14)
    ud_made, ud_opp = parse_ratio(args.updowns)
    gir_made, _ = parse_ratio(args.gir)

    r = {
        "date": args.date or date.today().isoformat(),
        "level": args.level,
        "score": args.score,
        "putts": args.putts,
        "fir_made": fir_made,
        "fir_holes": fir_holes or 14,
        "gir_made": gir_made,
        "ud_made": ud_made,
        "ud_opp": ud_opp,
        "penalties": args.penalties,
        "notes": (args.notes or "").strip(),
    }
    rounds = load()
    rounds.append(r)
    save(rounds)
    print(f"✓ Logged round: {r['date']} · {r['level']}"
          + (f" · {r['score']}" if r["score"] is not None else ""))
    print_breakdown(r)


def cmd_show(args):
    rounds = sorted(load(), key=lambda r: r["date"])
    if not rounds:
        print("No rounds logged yet. Log one, or hand Claude a photo of your scorecard.")
        return
    print(f"\n{len(rounds)} round{'s' if len(rounds) != 1 else ''} logged:\n")
    for r in rounds:
        cats = analyze(r)
        leak = max(cats.items(), key=lambda kv: kv[1]["lost"])[0] if cats else "—"
        score = r["score"] if r["score"] is not None else "?"
        note = f"  — {r['notes']}" if r["notes"] else ""
        print(f"   {r['date']}   score {score:<4} leak: {leak}{note}")
    scores = [r["score"] for r in rounds if isinstance(r["score"], (int, float))]
    if len(scores) >= 2:
        arrow = "↘ lower (good)" if scores[-1] < scores[0] else \
                "↗ higher" if scores[-1] > scores[0] else "→ flat"
        print(f"\n   score {scores[0]} → {scores[-1]}   {arrow}")
    print("\nRe-run the read after your next round and watch the biggest leak move.")


def main():
    ap = argparse.ArgumentParser(description="rangey round log — find your biggest leak")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", help="log a round and read your biggest leak")
    a.add_argument("--level", required=True, choices=list(BASELINES),
                   help="beginner / mid / low / scratch")
    a.add_argument("--score", type=int, help="total score for the round")
    a.add_argument("--putts", type=int, help="total putts")
    a.add_argument("--fir", help="fairways hit, e.g. 6/14")
    a.add_argument("--gir", help="greens in regulation hit, out of 18")
    a.add_argument("--updowns", help="up-and-downs made/attempted, e.g. 3/11")
    a.add_argument("--penalties", type=int, default=0, help="penalty strokes (OB/water)")
    a.add_argument("--date", help="YYYY-MM-DD (default: today)")
    a.add_argument("--notes", help="optional note")
    a.set_defaults(func=cmd_add)

    s = sub.add_parser("show", help="list rounds and the leak trend")
    s.set_defaults(func=cmd_show)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
