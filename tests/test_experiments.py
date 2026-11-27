import numpy as np
import pytest

from board import Board
from experiments import ROWS, COLS, SEED_CELLS, run_colony, threshold_policy


@pytest.mark.parametrize("density, expected", [
    (0.000, "SPORULATION"),
    (0.019, "SPORULATION"),
    (0.020, "NUTRIENT_BOOST"),     # boundary: 2% is no longer a crash
    (0.049, "NUTRIENT_BOOST"),
    (0.050, "HOMEOSTASIS"),        # boundary: 5% is no longer sparse
    (0.400, "HOMEOSTASIS"),        # boundary: cull only *above* 40%
    (0.401, "PHAGE_CULL"),
])
def test_threshold_policy_matches_the_prompt(density, expected):
    assert threshold_policy(density) == expected


def test_same_seed_gives_the_same_colony():
    assert np.array_equal(run_colony(7, 300, "threshold"), run_colony(7, 300, "threshold"))


def test_no_ai_policy_is_pure_physics():
    np.random.seed(3)
    board = Board.from_size(ROWS, COLS)
    board.seed_random(SEED_CELLS)
    expected = []
    for _ in range(120):
        board.step()
        expected.append(board.grid.mean())
    assert np.allclose(run_colony(3, 120, "none"), expected)


def test_withdrawal_matches_threshold_until_help_stops():
    helped = run_colony(5, 400, "threshold")
    withdrawn = run_colony(5, 400, "withdrawal", stop_at=200)
    assert np.array_equal(helped[:200], withdrawn[:200])
