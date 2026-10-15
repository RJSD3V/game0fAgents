# Conway's Game of Life — Test invariants
#
# Known fixtures (patterns with mathematically proven behaviour):
#
# BLOCK (still life):     ##      After any number of generations,
#                         ##      the block is unchanged. Each cell has
#                                 exactly 3 neighbours → all survive,
#                                 no dead cell has exactly 3 → no births.
#
# BLINKER (period 2):    gen 0    gen 1    gen 2 (== gen 0)
#                         ###      .#.      ###
#                                  .#.
#                                  .#.
#
# These are the two simplest Conway invariants. If either breaks,
# the transition function is wrong.

from board import Board, count_neighbors
import pytest
import numpy as np


@pytest.fixture
def board():
    return Board.from_size(100, 200)


def test_transposition():
    b = Board.from_size(10, 20)
    with pytest.raises(ValueError):
        b.place(19, 9)


def test_alive(board):
    board.place(10, 10)
    assert board.is_alive(10, 10)


def test_negative_index(board):
    with pytest.raises(ValueError):
        board.place(-1, -1)


def test_block_still_life():
    b = Board.from_size(6, 6)
    b.place(2, 2)
    b.place(2, 3)
    b.place(3, 2)
    b.place(3, 3)
    gen0 = b.grid.copy()
    b.step()
    assert np.array_equal(b.grid, gen0), "Block must be unchanged after one step"
    b.step()
    assert np.array_equal(b.grid, gen0), "Block must be unchanged after two steps"


def test_blinker_period_2():
    b = Board.from_size(7, 7)
    b.place(3, 2)
    b.place(3, 3)
    b.place(3, 4)
    gen0 = b.grid.copy()

    b.step()
    gen1 = b.grid.copy()
    assert not np.array_equal(gen0, gen1), "Blinker must change after one step"

    expected_gen1 = np.zeros_like(gen0)
    expected_gen1[2, 3] = 1
    expected_gen1[3, 3] = 1
    expected_gen1[4, 3] = 1
    assert np.array_equal(gen1, expected_gen1), "Blinker gen1 must be vertical"

    b.step()
    assert np.array_equal(b.grid, gen0), "Blinker must return to gen0 after two steps"


def test_empty_board_stays_empty():
    b = Board.from_size(10, 10)
    gen0 = b.grid.copy()
    b.step()
    assert np.array_equal(b.grid, gen0)


def test_lone_cell_dies():
    b = Board.from_size(10, 10)
    b.place(5, 5)
    b.step()
    assert not b.is_alive(5, 5), "Lone cell dies of underpopulation"
    assert b.grid.sum() == 0


def test_neighbor_count():
    grid = np.zeros((5, 5), dtype=np.int8)
    grid[2, 2] = 1
    neighbors = count_neighbors(grid)
    assert neighbors[1, 1] == 1
    assert neighbors[2, 2] == 0
    assert neighbors[1, 2] == 1
    assert neighbors[3, 3] == 1


def test_step_returns_correct_shape(board):
    board.seed_random(50)
    old_shape = board.grid.shape
    board.step()
    assert board.grid.shape == old_shape
