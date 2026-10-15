# Talk Notes — Community Talk, 2026-10-17

Running collection of ideas worth presenting. Captured as they come up while
building, because the good ones surface during debugging and are lost by evening.

Each entry: the **claim**, the **why**, and the **demo** that makes it land in a room.

---

## Double buffering is required, not stylistic

**Claim.** Conway's Game of Life cannot be computed in place. The two-array
approach isn't a coding preference — the rules *forbid* the one-array version.

**Why.** Every cell in generation N+1 must be computed against the *same*
generation N. If you mutate the board as you sweep it, a cell updated early
becomes a neighbour that a cell updated later reads — so the later cell is
counting a mixture of two generations. The sweep order silently becomes part of
the rules. Scan left-to-right and you get one universe; right-to-left, a
different one. Neither is Conway.

So you need the previous generation to stay intact until the whole new one is
built. Read from one buffer, write to the other, then swap. That's
**double buffering**.

**Demo.** Show the in-place version running. It looks plausible — cells live and
die, patterns move. Then put a glider on it. The glider mutates or dies, because
the scan direction leaks into the physics. Then show the same seed double-
buffered and the glider glides. Same rules, same seed, one line of difference.
That contrast is the whole point, and it's more convincing than any explanation.

**Biology hook.** Real cells face this too. Mitosis has checkpoints precisely
because a cell must not act on a half-replicated genome — the G1/S restriction
point (see [REFERENCE.md](REFERENCE.md), Rule 4) is a commit barrier. The
stringent response is a rollback. Cells don't do in-place updates either: DNA
replication is semiconservative, building a new strand against the old one
before the old one is released. Nature double-buffers.

**Vocabulary for the slide:** double buffering · immutability · atomic swap ·
read-write consistency · semiconservative replication.

---

## Never test an axis convention with a square fixture

**Claim.** If code has a notion of rows and columns, its tests must use unequal
row and column counts, or they prove nothing.

**Why.** A transposition bug is invisible on a square board — `arr[r][c]` and
`arr[c][r]` are both in-bounds, so the code silently swaps every coordinate and
never errors. Symmetry in a fixture hides any bug that is itself a symmetry.

**Demo.** Place cells on a 10×10 with the axes swapped: works fine, apparently.
Same code on a 3×12: `IndexError` on the first call, six times out of six. The
crash is the *good* outcome — the square board was lying.

---

## A test with no assertions always passes

**Claim.** Green is a claim. An empty test body makes that claim falsely, forever.

**Why.** pytest reports success when a test function returns without raising.
No assertions, no raise, so: PASSED. Whole suites have rotted this way — the
coverage number goes up while the evidence goes down.

**Demo.** A test function containing only a docstring, shown PASSED in the
terminal. Takes five seconds and lands hard.

---

## Debugging a pipeline: bisect the intermediates

**Claim.** When a chain `a → b → c` produces nothing, don't read the code —
print every intermediate and find the first wrong one.

**Why.** It converts "somewhere in this function" into "between these two lines"
in as many steps as log₂(stages). Two prints narrowed a dead `next_board` from a
whole function to a single character.

**Demo.** Live: the blinker's neighbour-count matrix (correct), after the birth
mask (correct), after the survival mask (unchanged — found it).

---

## Slide plan: what a cell is, and how a CA represents it

*Outline only — structure and facts. Wording on the slide is mine to write.*

**Purpose.** One slide for an audience that knows code but not biology. Three
jobs: what a cell is, how a cellular automaton maps onto one, and where the
field came from. The slide carries one picture and ~3 short lines; the rest is
spoken.

**Layout.**

```
┌──────────────────────────────────────────────────────────┐
│  [title: my one-line framing]                            │
│                                                          │
│   A REAL CELL          ──maps to──>   A GRID CELL        │
│   (image: bacterium)                  (image: 3×3 grid,  │
│                                        centre + 8 nbrs)  │
│                                                          │
│   senses nearby chemistry   →   reads its 8 neighbours   │
│   its chemistry reacts      →   applies 4 fixed rules    │
│   lives / divides / dies    →   alive or dead            │
│   (all cells, same moment)  →   whole grid updates       │
│                                                          │
│  footer: von Neumann 1948 → Conway 1970 → today          │
└──────────────────────────────────────────────────────────┘
```

**1. What a cell is** (one line, ~20s spoken)
- Smallest unit of life. A bacterium is ~1–2 µm — about 500 side by side
  span a millimetre.
- A membrane around chemistry plus genetic instructions.
- *The thesis fact:* no brain, no nervous system. It reacts only to molecules
  at its own surface — nutrients, toxins, signals from neighbours.

**2. How a CA represents it** (the table is the centrepiece)

| CA term | My code | The biology |
|---|---|---|
| State | 0 / 1 in the grid | alive / dead |
| Neighbourhood | the 8 surrounding squares | what the cell can sense nearby |
| Rule | the 4 Conway rules | its chemistry |
| Time step | one `step()` call | one generation |

Say aloud: it's a cartoon, not a simulation. What it keeps is the one constraint
that matters — **local information only.**

**3. The field** (footer + ~30s spoken; pick 2–3, not all)
- **1940s — von Neumann & Ulam.** Can a machine build a copy of itself? On a
  grid, von Neumann showed it needs instructions that are both *copied* and
  *read* — before DNA's structure was discovered (1953), which turned out to
  work that way.
- **1970 — Conway's Game of Life.** Popularised by Martin Gardner in
  *Scientific American*. Simplest rules that still produce surprising behaviour.
- **1980s–2000s — Wolfram, Rule 110.** A 1-D automaton proven Turing-complete.
  Use if making the "dumb rules can compute anything" point.
- **2020 — Neural Cellular Automata** (Mordvintsev et al., *Distill*, "Growing
  Neural Cellular Automata"). Learned rules grow a shape and regrow it when
  damaged — like tissue regeneration. Best bridge back to biology; runs in a
  browser.

**Pitfalls.**
- Too much text — if the slide reads without me, it's too dense. ≤8 words per
  line, three lines plus the table.
- Don't say "simulates cells." Say it *captures one constraint* of cells.
- No thinking-verbs: not "decides / knows / wants" — use "reads / reacts /
  applies." The thesis lives or dies on this.

**To write (me):**
- [ ] Title line
- [ ] The three slide lines
- [ ] Which 2–3 history points to keep
