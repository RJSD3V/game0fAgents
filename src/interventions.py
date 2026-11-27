"""Environmental events the quorum-sensing coordinator can trigger.

Each event edits a board between two generations and returns the cells it
changed, so the UI can highlight them. None of them touch the rules in
board.py: the AI changes the *state* of the colony, never the physics.

Used by both the live app (app.py) and the headless runner (experiments.py),
so an experiment measures exactly what the app does.
"""
import numpy as np

from board import Board

BOOST_CELLS = 40          # cells revived by a nutrient boost
CULL_RADIUS = 8           # a cull clears a 16 x 16 square
SPORULATION_CELLS = 80    # random positions scattered by sporulation

Cell = tuple[int, int]


def nutrient_boost(board: Board, n: int = BOOST_CELLS) -> list[Cell]:
    """Food arrives: bring up to `n` random dead cells to life."""
    dead = np.argwhere(board.grid == 0)
    if len(dead) == 0:
        return []
    picks = dead[np.random.choice(len(dead), min(n, len(dead)), replace=False)]
    board.grid[picks[:, 0], picks[:, 1]] = 1
    return [(int(r), int(c)) for r, c in picks]


def phage_cull(board: Board, radius: int = CULL_RADIUS) -> list[Cell]:
    """A phage outbreak: kill every live cell in a square around a random live cell."""
    live = np.argwhere(board.grid == 1)
    if len(live) == 0:
        return []
    r, c = live[np.random.randint(len(live))]
    top, left = max(0, r - radius), max(0, c - radius)
    window = board.grid[top:r + radius, left:c + radius]   # a view into the grid
    culled = np.argwhere(window == 1) + (top, left)
    window[:] = 0
    return [(int(r), int(c)) for r, c in culled]


def sporulation(board: Board, n: int = SPORULATION_CELLS) -> list[Cell]:
    """Dormant spores wake up: scatter `n` cells at random positions."""
    before = board.grid.copy()
    board.seed_random(n)
    born = np.argwhere((board.grid == 1) & (before == 0))
    return [(int(r), int(c)) for r, c in born]


EVENTS = {
    "NUTRIENT_BOOST": nutrient_boost,
    "PHAGE_CULL": phage_cull,
    "SPORULATION": sporulation,
}


def apply(decision: str, board: Board) -> list[Cell]:
    """Apply a coordinator decision. HOMEOSTASIS (or anything unknown) does nothing."""
    event = EVENTS.get(decision)
    return event(board) if event else []
