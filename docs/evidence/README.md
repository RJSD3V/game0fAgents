# Evidence

This folder backs every number in the [project README](../../README.md). For each claim it names the file that supports it, how to reproduce it, and any caveat.

| File | What it is | Reproduce with |
|---|---|---|
| [pytest-results.txt](pytest-results.txt) | The full test suite, verbose | `uv run pytest -v` |
| [experiment-results.json](experiment-results.json) | Output of the experiment runner: 30 seeded colonies per policy | `uv run python src/experiments.py` |
| [live-run-2026-11-27.log](live-run-2026-11-27.log) | Every AI request, raw Claude reply and applied decision from one live session | run the app |
| [result-claude-vs-baseline.png](../images/result-claude-vs-baseline.png), [result-withdrawal.png](../images/result-withdrawal.png) | The result charts presented at the talk on 2026-10-17 | n/a |

---

## The physics is correct

**Claim:** the Game of Life implementation reproduces known patterns and handles its boundaries.

**Evidence:** [pytest-results.txt](pytest-results.txt). All 27 tests pass, including:
- a block that never changes
- a blinker with an exact period of 2
- a lone cell that dies
- out-of-bounds placement that is rejected
- an axis-convention test on a non-square board

## Without help, the colony collapses

**Claim:** average density is about 0.8%.

**Evidence:** [experiment-results.json](experiment-results.json), `no_ai`. The median is **0.77%** (interquartile range 0.42–1.21%), measured from generation 1,000 to 10,448 across 30 seeds. The talk chart showed 0.7%.

## A simple `if` statement keeps it alive

**Claim:** the prompt's thresholds, written as plain code, hold density at about 5.8%.

**Evidence:** `threshold`. The median is **5.79%** (interquartile range 5.54–5.99%).

**Caveat:** the talk chart showed 5.4%. The runner applies each decision instantly, while the version behind the chart had some lag, and the random seeds differ. Both agree on the shape of the result.

## Claude does about as well

**Claim:** Claude holds density at about 5.6%.

**Evidence:**
- **Talk chart:** 5.6% mean over generations 1,000–10,448, from one live run.
- **Live log:** in [live-run-2026-11-27.log](live-run-2026-11-27.log), density at the 11 AI checkpoints from generation 1,000 onwards averages **5.6%**.

**Caveat:** both figures come from single live runs. They support "about the same as the `if` statement", not "better" or "worse".

## Help is life support

**Claim:** stop helping at generation 5,000 and density falls from about 5.7% to 2.8%.

**Evidence:** `withdrawal_during_help` has a median of **5.72%** (generations 1,000–5,000). `withdrawal_last_1000` has a median of **2.80%**. The talk chart showed 5.3% → 2.8%.

## What went wrong with the AI

All from [live-run-2026-11-27.log](live-run-2026-11-27.log), which covers 20 AI calls over about 1,800 generations.

- **Stale decisions:** each decision landed 24–155 generations (median about 58) after the snapshot it was based on. Only 20 of the 35 scheduled checkpoints fired. The others were skipped because the previous call was still running.
- **Format failure:** at the generation-1,750 checkpoint, Claude wrote a sentence before its JSON. The parser rejected the reply and the engine fell back to "do nothing", discarding a valid `NUTRIENT_BOOST`.
- **Threshold-following:** every reasoning string quotes the prompt's thresholds. For example, Claude chose `SPORULATION` at 0.5% density, citing "below the 2% crash threshold".

The "ten consecutive interventions, there were two" example in the README comes from a Langfuse trace shown at the talk. That trace isn't in this folder.

---

**How the log was cleaned:** ClickHouse and Langfuse were offline for that session. Their connection-error tracebacks were removed and home-directory paths shortened. Every `[ai]` and `[workflow]` line is kept exactly as printed.
