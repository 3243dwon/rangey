#!/usr/bin/env python3
"""
practice_log — the adaptive loop for the rangey skill.

Logs each practice session's focus and pressure-test score, then shows the
trend on a given skill over time so the next session can be adjusted. Plain
JSON storage, zero dependencies.

Usage:
    python practice_log.py add --focus putting --score 7 --notes "make-10 from 4ft"
    python practice_log.py show
    python practice_log.py show --focus putting
    python practice_log.py list

Scores are whatever the session's pressure test produced (a count, a percent,
a points total) — consistency per focus is what matters, not the unit.
"""

import argparse
import json
import os
import sys
from datetime import date

LOG_PATH = os.environ.get("RANGEY_LOG", "practice_log.json")


def load():
    if not os.path.exists(LOG_PATH):
        return []
    try:
        with open(LOG_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        print(f"⚠  Could not read {LOG_PATH}; starting fresh.", file=sys.stderr)
        return []


def save(entries):
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)


def fmt_score(s):
    """Show whole numbers as ints (7, not 7.0); keep genuine decimals."""
    if isinstance(s, float) and s.is_integer():
        return str(int(s))
    return str(s)


def cmd_add(args):
    entries = load()
    entry = {
        "date": args.date or date.today().isoformat(),
        "focus": args.focus.strip().lower(),
        "score": args.score,
        "notes": (args.notes or "").strip(),
    }
    entries.append(entry)
    save(entries)
    print(f"✓ Logged: {entry['date']} · {entry['focus']} · score {fmt_score(entry['score'])}"
          + (f" · {entry['notes']}" if entry['notes'] else ""))


def trend_arrow(scores):
    """Compare the latest score to the mean of the prior ones."""
    if len(scores) < 2:
        return ""
    prior = scores[:-1]
    avg = sum(prior) / len(prior)
    latest = scores[-1]
    if latest > avg + 0.01:
        return "↗ improving"
    if latest < avg - 0.01:
        return "↘ slipping"
    return "→ flat"


def cmd_show(args):
    entries = load()
    if not entries:
        print("No sessions logged yet. Go practice, then log it.")
        return

    if args.focus:
        focus = args.focus.strip().lower()
        rows = [e for e in entries if e["focus"] == focus]
        if not rows:
            print(f"No sessions logged for '{focus}'.")
            return
        foci = {focus: rows}
    else:
        foci = {}
        for e in entries:
            foci.setdefault(e["focus"], []).append(e)

    for focus, rows in foci.items():
        rows = sorted(rows, key=lambda e: e["date"])
        scores = [r["score"] for r in rows if isinstance(r["score"], (int, float))]
        print(f"\n● {focus.upper()}  ({len(rows)} session{'s' if len(rows) != 1 else ''})  "
              f"{trend_arrow(scores)}")
        for r in rows:
            spark = "▮" * int(min(r["score"], 20)) if isinstance(r["score"], (int, float)) else ""
            note = f"  — {r['notes']}" if r["notes"] else ""
            print(f"   {r['date']}   score {fmt_score(r['score']):<4} {spark}{note}")
        if len(scores) >= 2:
            best = max(scores)
            print(f"   best: {fmt_score(best)}   latest: {fmt_score(scores[-1])}")

    print("\nFeed this trend back into the next session: improving → harder; "
          "flat → change the drill or go more random.")


def cmd_list(args):
    entries = sorted(load(), key=lambda e: e["date"])
    if not entries:
        print("No sessions logged yet.")
        return
    for e in entries:
        note = f"  — {e['notes']}" if e["notes"] else ""
        print(f"{e['date']}  {e['focus']:<12} score {fmt_score(e['score'])}{note}")


def main():
    ap = argparse.ArgumentParser(description="rangey practice log")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", help="log a session")
    a.add_argument("--focus", required=True, help="skill worked, e.g. putting")
    a.add_argument("--score", required=True, type=float, help="pressure-test score")
    a.add_argument("--date", help="YYYY-MM-DD (default: today)")
    a.add_argument("--notes", help="optional note")
    a.set_defaults(func=cmd_add)

    s = sub.add_parser("show", help="show trend(s)")
    s.add_argument("--focus", help="limit to one skill")
    s.set_defaults(func=cmd_show)

    l = sub.add_parser("list", help="list all sessions")
    l.set_defaults(func=cmd_list)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
