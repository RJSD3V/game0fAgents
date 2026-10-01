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

from board import Board, next_board
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
    """ testing if a newly created cell is instantiated as an alive cell"""
    board.place(10, 10)
    assert board.is_alive(10,10)

def test_blinker(board):
    """ Test inline cells"""
    board.place(10,11)
    board.place(10,12)
    board.place(10,13)
    x = next_board(board.grid)
    assert not np.array_equal(board.grid,x)


def test_negative_index(board):
    loc_x = -1
    loc_y = -1

    with pytest.raises(ValueError):
        board.place(-1,-1)



    


    