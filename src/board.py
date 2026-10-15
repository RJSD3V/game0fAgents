# Conway's Game of Life — Rules
#
# 1. BIRTH:      A dead cell with exactly 3 live neighbours becomes alive.
# 2. SURVIVAL:   A live cell with 2 or 3 live neighbours stays alive.
# 3. DEATH:      A live cell with fewer than 2 neighbours dies (underpopulation).
# 4. DEATH:      A live cell with more than 3 neighbours dies (overcrowding).
#
# All cells are evaluated simultaneously against the SAME generation.
# (Double buffering: read from the current board, write to a new one, then swap.)

import numpy as np


class Board:
    def __init__(self, default:np.ndarray=None):
        self.grid = default
        self.size = {'rows': default.shape[0], 'cols': default.shape[1]}
    
    @classmethod
    def from_size(cls,rows,cols):
        grid = np.zeros(shape=(rows,cols), dtype=np.int8)     
        return cls(default=grid)
            
        
    def place(self, row, col):
        if (row <0 or row>self.size['rows']-1):
            raise ValueError("Value needs to be valid and Non-negative")
        if (col < 0 or col>self.size['cols']-1):
            raise ValueError("Value needs to be valid and Non-Negative")
        if self.grid[row][col] == 0:
            self.grid[row][col] = 1

    def seed_random(self,n=1):
        for i in range(0,n):
            row_pos= np.random.randint(low=0, high=self.size['rows'])
            col_pos = np.random.randint(low=0,high=self.size['cols'])
            self.grid[row_pos][col_pos] = 1 if self.grid[row_pos][col_pos] == 0 else 0
        
    def is_alive(self, r,c) -> bool:
        return bool(self.grid[r][c])
    

    def show(self):
        print('\n')
        print(self.grid)
        print('\n')

    def step(self):
        self.grid = next_board(grid = self.grid)

def count_neighbors(grid: np.ndarray) -> np.ndarray:
    neighbors = np.zeros_like(grid)
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            neighbors += np.roll(np.roll(grid, dr, axis=0), dc, axis=1)
    return neighbors



def next_board(grid: np.ndarray) -> np.ndarray:
    neighbors = count_neighbors(grid)
    birth = (grid == 0) & (neighbors == 3)
    survive = (grid == 1) & ((neighbors == 2) | (neighbors == 3))
    return (birth | survive).astype(grid.dtype)


def main():
    b = Board.from_size(10,10)
    b.place(5,5)
    b.step()
    b.show()
    b.place(5,4)
    b.step()
    b.show()
    b.place(5,3)
    b.step()
    b.show()
    


    
    

if __name__ == '__main__':
    main()