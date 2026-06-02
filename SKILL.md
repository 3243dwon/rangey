---
name: range-rat
description: Generate adaptive, science-based golf practice sessions tailored to a player's specific weakness, available time, and resources — using motor-learning principles (blocked vs. random vs. pressure practice) instead of mindless ball-beating. Use whenever someone wants to plan golf practice, asks what to work on, has limited range time and a bucket of balls, wants to fix a specific part of their game (slice, short game, putting, approach, driving), or wants practice that actually transfers to the course. Trigger on phrases like "what should I practice", "plan my range session", "I have 30 minutes at the range", "help me fix my slice", "golf practice plan", "make my practice count", "here's my scorecard — what should I work on", "what's costing me the most strokes", or any request to turn a round's results (or a scorecard photo) into a practice focus.
---

# Range Rat

Most golfers waste the range. They beat a bucket of balls with the driver, feel good, and then spray it on Saturday. This skill exists to fix that — by building practice sessions the way motor-learning research says skills actually transfer, not the way that *feels* productive.

It is **not a drill library** (those already exist, mostly paywalled). It's an adaptive system: it aims practice at where strokes are actually lost, structures it by the science of skill acquisition, ends every session with a measurable test, and adjusts over time.

## Core principles (the science)

These four ideas are the whole differentiator. Apply them every time.

### 1. Aim at where strokes are actually lost — not where it's fun
Amateur instinct is to bash drivers. But the data (Broadie's strokes-gained work) is blunt: for most amateurs, **approach shots and the short game inside 100 yards cost the most strokes**, not driving. Unless the player has a specific full-swing leak, default the allocation toward approach, wedges, and putting. Resist the driver-bias.

### 2. Block to learn, random to transfer
This is the single most-missed idea in golf practice:

- **Blocked practice** (same shot, same club, repeated) feels great and improves you fast *in the session* — but it transfers poorly to the course, where you never hit the same shot twice. Use it **sparingly**: only to ingrain a brand-new movement or feel, and only at the start (cap ~20% of a session).

- **Random / interleaved practice** (change target, club, or shot every single rep) feels worse and looks messier — but it produces far better **retention and on-course transfer**. It mimics real golf. This should be the **bulk** of most sessions.

- **Variable practice** (vary distance/trajectory within one skill) builds adaptability — useful for dialing in wedges and approach.

If someone is grooving a swing change, lean blocked early then shift to random. If they're preparing to *play*, lean random.

### 3. End with pressure, and keep score
Practice without consequences doesn't prepare you for the first tee. Every session ends with a **pressure test**: a game with a score, a target percentage, or a "must-make" — something that creates a little discomfort and produces **a number**. That number is the session's outcome and the thing you track.

### 4. Quality over quantity
Focused, deliberate reps at the edge of ability beat mindless volume. A sharp 45-minute session beats two aimless hours — and protects against the overuse injuries that come from hammering hundreds of full-swing balls.

## Required inputs

Establish before building (ask only what you can't infer):

1. **Level** — handicap or rough ability (beginner / mid / low / scratch). Drives difficulty and the block-vs-random ratio.
2. **Focus** — the weakness or goal. Either stated ("fix my slice", "100-yard wedges") or derived from a round's results ("you lost most strokes around the green").
3. **Time available** — drives the structure and how many blocks fit.
4. **Resources / location** — full range, putting green, chipping area, home/net, or simulator. Only prescribe what they can actually do.

If focus is unclear, ask one question or infer from round data; if you have stats, name the biggest leak yourself.

## From a round to the focus (the data hook)

The strongest input is a real round. If the player hands you a **photo of their scorecard** — or even a few stats they remember — don't eyeball it. Quantify the leak:

1. **Read the card.** Pull what's on it: per-hole score and putts, fairways hit, greens in regulation, penalties, and up-and-downs if marked. A plain card gives score + putts; a stats card gives all of it. If there's no photo, ask only for the few numbers they can recall.
2. **Run the read.** Feed the round to `scripts/round_log.py`. It compares the stats to a baseline for the player's level and estimates which part of the game is losing the most strokes:

```bash
python scripts/round_log.py add --level mid --score 92 --putts 37 \
    --fir 7/14 --gir 6 --updowns 3/12 --penalties 1
```

It prints a *where your strokes go* breakdown, names the biggest leak, and maps it to a focus. **That leak is the session's focus** — then build the session exactly as below.
3. **Close the loop across rounds.** After the player practices the leak and plays again, re-run the read: the biggest leak should move and the score should follow. Reference that movement, don't start cold.

Be honest that this is a transparent approximation, not shot-by-shot strokes-gained — it's built to find the *biggest* leak from stats a player can actually produce, which is exactly what's needed to aim one session.

## Building a session

1. **Pick the priority leak.** From their input or round data. One primary focus per session — scattershot sessions don't work.
2. **Allocate time** weighted toward the leak and toward where strokes are lost (principle 1).
3. **Sequence by the science**: brief warm-up → optional short blocked segment (only if grooving something new) → the main random/transfer work → a scored pressure test to finish.
4. **Make every block concrete**: specific drill, rep count or duration, a target, and a clear success criterion. Vague ("work on putting") is useless; specific ("make 10 in a row from 4 ft, restart on a miss") is practice.
5. **Set the test + what to log**: the end-game score, and the one number to record so next session adapts.

## Output format

Deliver a clean, time-boxed session:

**🎯 Focus:** [the one priority] — *why (1 line, tied to where strokes are lost or their stated leak)*

**🕒 Session ([total time], [location]):**

For each block:
> **[Block name] — [minutes]** · *[block / random / variable / pressure]*
> [Specific drill, reps/duration, target, success criterion]

End with:

**🔥 Pressure test:** [a scored game — the session finisher] → **log this score**

**📈 Next time:** [one line — how the result should shift the next session]

Keep it tight and doable. A player should be able to glance at it at the range and go.

## A starter bank of real drills (draw from these, don't dump them)

**Putting** — Ladder drill (distance control, vary length each putt); Clock drill (short putts around the hole, random positions); Make-10-from-4ft (pressure, restart on miss); Lag to a 3-ft circle from 30/40/50 ft (random distances).

**Short game** — Par-18 (pick 9 up-and-downs around the green, par is 2 each = 18, play them random); Landing-zone targets (land it in a towel/circle, not just "near the hole"); Three clubs one lie (chip with three different clubs from the same spot — variable).

**Approach / wedges** — Random number game (caller or app gives you a yardage every shot, never repeat); 9-window (3 trajectories × 3 distances — advanced); Closest-to-pin scored over 10 random targets.

**Full swing / driver** — Random target + shot-shape call before each ball (commit, then judge); Fairway-finder % (define a fairway width, track hit %); Worst-ball pressure (your miss has to still be playable).

These are seeds. Tailor difficulty to level and keep the bulk random.

## The adaptive loop

This skill bundles two zero-dependency trackers. `scripts/round_log.py` (above) turns a round into your biggest leak; `scripts/practice_log.py` logs each session's focus and pressure-test score and shows the trend on a skill over time. Together they close the full loop: **round → leak → targeted practice → pressure-test score → next round.**

```bash
python scripts/practice_log.py add --focus putting --score 7 --notes "make-10 from 4ft"
python scripts/practice_log.py show --focus putting
```

Use the log to close the loop:
- **Score improving** → nudge difficulty up or graduate to a harder game.
- **Score plateaued over several sessions** → change the drill or the practice mode (often: more random, less blocked).
- **A different leak now dominates** (from new round data) → switch the focus.

When a player returns, check the log first and reference their trend rather than starting cold.

## Calibration notes

- **Match level.** Beginners need more blocked work and simpler pressure games; better players need mostly random practice and harder tests. Don't hand a 25-handicap a tour-level 9-window drill.
- **Match resources.** Don't prescribe bunker drills to someone on a mat at home. Ask or assume conservatively.
- **One focus per session.** Spreading thin is the default failure mode — protect against it.
- **Transfer, not feelings.** If a session looks fun and tidy but is all blocked, it's wrong. Discomfort and messiness in practice is often the sign it'll hold up on the course.
- **This is practice guidance, not swing instruction or medical advice.** Don't diagnose mechanics from text; focus on *how to practice*. Flag that high-volume full-swing work carries overuse-injury risk and quality beats quantity.
