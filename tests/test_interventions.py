import numpy as np
import pytest

import interventions
from board import Board


@pytest.fixture(autouse=True)
def fixed_seed():
    np.random.seed(0)


def test_nutrient_boost_revives_exactly_n_dead_cells():
    board = Board.from_size(10, 12)
    changed = interventions.nutrient_boost(board, n=40)
    assert board.grid.sum() == 40
    assert len(set(changed)) == 40
    assert all(board.grid[r, c] == 1 for r, c in changed)


def test_nutrient_boost_on_full_board_does_nothing():
    board = Board(np.ones((5, 5), dtype=np.int8))
    assert interventions.nutrient_boost(board) == []
    assert board.grid.sum() == 25


def test_phage_cull_kills_only_inside_its_square():
    board = Board(np.ones((40, 50), dtype=np.int8))
    culled = interventions.phage_cull(board, radius=8)
    assert 0 < len(culled) <= 16 * 16
    assert all(board.grid[r, c] == 0 for r, c in culled)
    assert board.grid.sum() == 40 * 50 - len(culled)   # nothing else touched


def test_phage_cull_on_empty_board_does_nothing():
    board = Board.from_size(10, 10)
    assert interventions.phage_cull(board) == []


def test_sporulation_reports_the_cells_it_created():
    board = Board.from_size(30, 40)
    born = interventions.sporulation(board, n=80)
    assert 0 < len(born) <= 80
    assert board.grid.sum() == len(born)


@pytest.mark.parametrize("decision", ["HOMEOSTASIS", "NOT_A_DECISION", ""])
def test_non_events_leave_the_board_alone(decision):
    board = Board.from_size(10, 10)
    board.place(5, 5)
    before = board.grid.copy()
    assert interventions.apply(decision, board) == []
    assert np.array_equal(board.grid, before)
