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

def next_board(grid: np.ndarray):
    def moore_nb(row,col,b):
        # Sequence goes top,a nd moves anti-clockwise
        n_count = 0
        nbrs  = [(row-1,col), (row-1,col-1),(row,col-1), (row+1,col-1),(row+1,col),(row+1,col+1),(row,col+1),(row-1,col+1)]
        for (ix,iy) in nbrs:
            if 0<=ix < b.shape[0] and 0<= iy < b.shape[1]:
                if b[ix][iy] == 1:
                    n_count +=1

        return n_count
    matrix = grid
    moore_nb_vec = np.vectorize(moore_nb, excluded=[2])
    neighbor_matrix = np.fromfunction(lambda x,y: moore_nb_vec(x,y,matrix),shape=matrix.shape, dtype=int)
    birth_condition = (neighbor_matrix == 3)
    survival_mask = (neighbor_matrix == 2) | (neighbor_matrix == 3)
    next_board = np.zeros_like(matrix)
    next_board[(matrix == 0) & birth_condition] = 1
    next_board[(matrix==1) & survival_mask] = 1
    return next_board


def main():
    b = Board.from_size(10,10)
    b.put_cell(5,5)
    b.step()
    b.show()
    b.put_cell(5,4)
    b.step()
    b.show()
    b.put_cell(5,3)
    b.step()
    b.show()
    


    
    

if __name__ == '__main__':
    main()