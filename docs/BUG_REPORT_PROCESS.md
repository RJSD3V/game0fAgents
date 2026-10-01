# How to find bugs in this project without help

Everything in the defect ledger was found with `python -c`, `pytest`, and reading.
No AI, no debugger, no paid tool. What follows is the whole method, in the order
you'd use it. It is a skill, not a talent — the leverage is entirely in *asking a
question that can be proved wrong and then paying twenty seconds to answer it.*

Run everything from the project root with the project venv.

---

## 0. The one habit that matters most: the throwaway probe

Stop reading code to decide whether it works. **Run it and print things.**

```bash
python -c "
import sys; sys.path.insert(0,'src')
from board import Board
b = Board(3, 12)
b.put_cell(0, 7)
print(b.grid)
"
```

That is the whole trick. A shell, an import, a print. You already have the habit
in a different form — `src/notebooks/game.ipynb` is exactly this environment.
You've been using it to *build*. Point it at *doubt* as well.

Variants worth knowing:

| Tool | Use |
|---|---|
| `python -c "..."` | one-shot probe, disposable, nothing to clean up |
| `python -i script.py` | run a file, then land in a REPL with everything still loaded |
| `breakpoint()` in the code | drops into `pdb` at that line; `p expr`, `n`, `c`, `q` |
| `pytest --pdb` | drops into `pdb` at the point of failure |
| `pytest -x -k blinker -vv` | stop at first failure, only matching tests, full diffs |
| the notebook | same as `python -c` but you keep the state between attempts |

Learn `pdb`'s four commands and you will rarely need anything heavier.

---

## 1. Scope the change before reading anything

```bash
git status --porcelain     # untracked files show as ?? — git diff hides them
git diff --stat
git diff
```

State the scope in the report, including **what you did not look at**. An
inventory that doesn't admit its gaps invites you to trust it too far.

---

## 2. Write hypotheses as falsifiable predictions

Not "the constructor looks sketchy." Instead:

> "`Board(3, 3, default=<10x20 array>)` will produce a 10×20 board and not
> complain — prediction: `grid.shape == (10, 20)`."

If you can't phrase it as a prediction with an expected output, it's a feeling,
not a hypothesis. Feelings are fine as a starting point; they just don't go in a
report.

Write five or six before you test any of them. Batching stops you from falling
down the first hole you find.

---

## 3. Prove each one. Do not skip this because the bug is obvious.

Obvious-looking bugs are the ones that turn out to be wrong. Run the cheapest
experiment that could **falsify** your claim, and record the command and output
verbatim.

| Claim | Cheapest proof |
|---|---|
| Wrong output | construct the failing input, run it |
| Crash | trigger it, capture the traceback |
| Slow | time both paths, report the ratio |
| Silently wrong | print the intermediate that should have changed |
| Assumption baked in | sweep the input space in a loop |
| Type confusion at a seam | print `type(x)`, `x.shape`, `repr(x)` |

### 3a. Sweep the input space instead of testing one value

This is how the hardcoded `(10, 10)` fell out. One loop, one printed table:

```bash
python -c "
import sys; sys.path.insert(0,'src')
import numpy as np
from board import next_board
for shape in [(10,10),(3,12),(20,20),(5,5),(1,10),(1,1)]:
    g = np.zeros(shape, dtype=np.int8)
    try:
        print(f'{str(shape):>9} -> OK, out {next_board(g).shape}')
    except Exception as e:
        print(f'{str(shape):>9} -> {type(e).__name__}: {str(e)[:60]}')
"
```

Twenty seconds, and it covers six cases instead of one. Any function taking a
size, a length, a count or a rate deserves this loop.

### 3b. Probe the boundaries, always

Bugs live at the edges. For any index or range, try: **`-1`, `0`, `1`, `n-1`,
`n`, `n+1`, and empty.** That is where the negative-index wraparound came from —
I didn't reason it out, I just tried `-1` because `-1` is always on the list.

### 3c. Measure, never estimate

"Slow" is not a finding. `0.290 ms → 726 ms extrapolated → 1.4 generations per
second` is a finding.

```bash
python -c "
import sys; sys.path.insert(0,'src')
import numpy as np, timeit
from board import next_board
g = np.zeros((10,10), dtype=np.int8); g[5,4]=g[5,5]=g[5,6]=1
for run in (1, 2):
    t = timeit.timeit(lambda: next_board(g), number=200)/200
    print(f'run {run}: {t*1000:.3f} ms')
"
```

**Always run it twice.** The first number can include one-time cost — imports,
JIT, cache fill, a connection. Reporting a cold number as steady state is the
most common embarrassing error in performance work.

### 3d. Bisect the intermediates

When a pipeline `a → b → c` produces nothing, don't read it. Print every stage
and find the **first one that's wrong**; the bug is between that stage and the
one before it. Two prints reduced a dead `next_board` to a single character.
Works on numpy chains, request middleware, ETL stages, build steps.

---

## 4. Try to disprove your own findings

The single most valuable step, and the one everyone skips.

For every defect you think you found, ask what would have to be true for it to be
*fine*, and check that. Two of my hypotheses died this way: I expected the Moore
neighbour list to be off by one (it's canonically correct) and I expected the
edge handling to wrap (it doesn't — it's a proper dish).

**Put the disproven ones in the report.** A report with no disproven hypotheses
looks like nothing was actually tested. And a reader who finds one bogus entry
stops trusting all the others — so three proven defects beat twelve speculative
ones every time.

---

## 5. Order by how quietly it breaks, not by how interesting it is

```
silent wrong answers   >   crashes
```

A crash announces itself. A wrong answer gets believed, acted on, and built upon.
Nobody is looking for it. So: silent first, always.

---

## 6. Let free tools find what your eyes can't

Some defect classes are functionally invisible to human reading. Don't try
harder — install the tool.

```bash
uv add --dev ruff mypy
ruff check src/ tests/        # ~800 lint rules
mypy src/                     # checks the type hints you already wrote
pytest -q                     # the suite
python -W error -c "..."       # turn warnings into errors
```

- **`ruff`** — catches `x == 1` written where `x = 1` was meant (an expression
  statement with no effect), unused imports, shadowed names. It would have found
  the survival-line bug instantly. Milliseconds to run.
- **`mypy`** — catches passing a `Board` where an `ndarray` is annotated. This is
  the entire payoff of writing annotations; without a checker they are only
  comments.
- **`python -W error`** — promotes silent warnings into loud tracebacks.

Wire `ruff` and `mypy` into a pre-commit hook and the boring half of code review
happens without you.

---

## 7. Occasionally, ask the code about itself

For questions about *your source* rather than its behaviour, parse it. This is
how the "`test_blinker` has zero assertions" finding was counted:

```bash
python -c "
import ast
tree = ast.parse(open('tests/test_board.py').read())
for fn in [n for n in tree.body if isinstance(n, ast.FunctionDef)]:
    n = sum(1 for x in ast.walk(fn) if isinstance(x, ast.Assert))
    print(f'{fn.name:>20}: {n} assertions')
"
```

Niche, but the idea generalises: the standard library can read your code as data.
`ast`, `inspect`, `dis` and `gc` answer questions no amount of scrolling will.

---

## 8. Write each finding so it teaches

Four parts. The last two are what make it worth keeping:

1. **What breaks** — concrete inputs, actual wrong outcome. Not "may cause issues
   under load."
2. **Evidence** — the command and its output, verbatim, with `file:line`. A
   reader must be able to re-run it.
3. **Why it happens** — the *mechanism*, and **name the concept**: incomplete
   refactor, check-then-act, mutually exclusive arguments, failing far from the
   cause. Named things become things you can spot again.
4. **How to catch it next time** — one generalisable question you could have
   asked. "Is that bounds check two-sided?" This is the part that compounds.

---

## The quality bar

- No claim without evidence. If you didn't run it, label it **plausible**.
- No adjectives standing in for measurements. "Slow", "often", "large" are
  placeholders for numbers you didn't collect.
- Cold-start checked — did you run it twice?
- Every finding names its mechanism. If you can't explain *why* it breaks, you
  found a symptom, not a bug.
- Disproven hypotheses included.
- Scope stated, gaps admitted.
- No padding with style nits. Report defects; mention cleanups separately and
  briefly.

---

## Report log

| Date | Scope | Report |
|---|---|---|
| 2026-09-26 | `src/board.py`, `tests/test_board.py` (uncommitted) | [Board Defect Ledger](https://claude.ai/artifact/VvLAxuMBtCepstBvA3KzeW) — 5 confirmed (3 silent), 4 quality, 3 disproven |
