"""Headless experiment runner: does an intervention policy keep the colony alive?

Runs the app's physics (board.py) and interventions (interventions.py) with no
window and no LLM, many times over with fixed seeds, and reports the colony's
density under three policies:

    none        Conway's rules only (the control)
    threshold   the thresholds from Claude's prompt as plain if-statements
                (the baseline Claude is compared against)
    withdrawal  threshold until --stop-at, then nothing

Usage, from the repo root:

    uv run python src/experiments.py                              # full run, ~2 min
    uv run python src/experiments.py --runs 5 --generations 6000  # quick look
    uv run python src/experiments.py --out docs/evidence/experiment-results.json
"""
import argparse
import json

import numpy as np

import interventions
from board import Board

ROWS, COLS = 60, 80     # same board as the app
SEED_CELLS = 300        # same starting colony as the app
INTERVAL = 50           # generations between decisions, as in the app


def threshold_policy(density: float) -> str:
    """The rules written into Claude's prompt, as code."""
    if density < 0.02:
        return "SPORULATION"
    if density < 0.05:
        return "NUTRIENT_BOOST"
    if density > 0.40:
        return "PHAGE_CULL"
    return "HOMEOSTASIS"


def run_colony(seed: int, generations: int, policy: str = "none",
               stop_at: int | None = None) -> np.ndarray:
    """Simulate one colony and return its density after every generation."""
    np.random.seed(seed)
    board = Board.from_size(ROWS, COLS)
    board.seed_random(SEED_CELLS)

    density = np.empty(generations)
    for gen in range(1, generations + 1):
        board.step()
        if gen % INTERVAL == 0 and _intervening(policy, gen, stop_at):
            interventions.apply(threshold_policy(board.grid.mean()), board)
        density[gen - 1] = board.grid.mean()
    return density


def _intervening(policy: str, gen: int, stop_at: int | None) -> bool:
    if policy == "threshold":
        return True
    if policy == "withdrawal":
        return gen <= stop_at
    return False


def summarise(values) -> dict:
    """Median and interquartile range across runs, as percentages."""
    pct = np.asarray(values) * 100
    return {
        "median": round(float(np.median(pct)), 2),
        "p25": round(float(np.percentile(pct, 25)), 2),
        "p75": round(float(np.percentile(pct, 75)), 2),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs", type=int, default=30, help="colonies per policy (seeds 0..runs-1)")
    parser.add_argument("--generations", type=int, default=10_448)
    parser.add_argument("--burn-in", type=int, default=1_000, help="generations ignored before measuring")
    parser.add_argument("--stop-at", type=int, default=5_000, help="when the withdrawal policy stops helping")
    parser.add_argument("--out", help="write the results as JSON to this path")
    args = parser.parse_args()

    if not args.burn_in < args.stop_at < args.generations - 1_000:
        parser.error("need burn-in < stop-at < generations - 1000")

    seeds = range(args.runs)
    runs = {}
    for policy in ("none", "threshold", "withdrawal"):
        print(f"running {args.runs} colonies with policy '{policy}'...")
        runs[policy] = [run_colony(s, args.generations, policy, args.stop_at) for s in seeds]

    start, stop = args.burn_in, args.stop_at
    results = {
        "no_ai": summarise([d[start:].mean() for d in runs["none"]]),
        "threshold": summarise([d[start:].mean() for d in runs["threshold"]]),
        "withdrawal_during_help": summarise([d[start:stop].mean() for d in runs["withdrawal"]]),
        "withdrawal_last_1000": summarise([d[-1_000:].mean() for d in runs["withdrawal"]]),
    }

    labels = {
        "no_ai": "No AI (control)",
        "threshold": "If-statement policy",
        "withdrawal_during_help": f"Withdrawal, generations {start:,}-{stop:,}",
        "withdrawal_last_1000": "Withdrawal, last 1,000 generations",
    }
    print(f"\nMean colony density, median of {args.runs} runs (interquartile range)\n")
    for key, label in labels.items():
        r = results[key]
        print(f"  {label:<38} {r['median']:>5.2f}%   ({r['p25']:.2f}-{r['p75']:.2f})")

    if args.out:
        config = {k: v for k, v in vars(args).items() if k != "out"}
        config.update(board=f"{ROWS}x{COLS}", seed_cells=SEED_CELLS, interval=INTERVAL)
        with open(args.out, "w") as f:
            json.dump({"config": config, "results": results}, f, indent=2)
        print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
