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


@pytest.fixture
def board():
    return Board.from_size(100, 200)

def test_transposition():
    b = Board.from_size(10, 20)
    with pytest.raises(IndexError):
        b.place(19, 9)

def test_alive(board):
    """ testing if a newly created cell is instantiated as an alive cell"""
    board.place(10, 10)
    assert board.is_alive(10,10)

def test_blinker():
    """ Test inline cells"""
    b = Board.from_size(10,10)
    b.place(5,5)
    b = next_board(b)
    b.show()
    b.place(5,4)
    b = next_board(b)
    b.show()
    b.place(5,3)
    b = next_board(b)
    b.show()

def test_negative_index(board):
    loc_x = -1
    loc_y = -1
    assert  loc_x >= 0 and loc_y >= 0
    board.place(loc_x, loc_y)
    board.show()



    


    