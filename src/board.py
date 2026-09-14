import numpy as np

class Board:
    def __init__(self, m,n):
        self.board = np.zeros(shape=(m,n), dtype=np.int8)
    def put_cell(self):
        ypos= np.random.randint(low=0, high=self.board.shape[0])
        xpos = np.random.randint(low=0,high=self.board.shape[1])
        print(ypos)
        print(xpos)
        self.board[xpos][ypos] = 1
    def show(self):
        print(self.board)

    def next_board(self, neighbor_matrix):
        def moore_nb(self,x,y,b):
            # Sequence goes top,a nd moves anti-clockwise
            n_count = 0
            nbrs  = [(x-1,y), (x-1,y-1),(x,y-1), (x+1,y-1),(x+1,y),(x+1,y+1),(x,y+1),(x-1,y+1)]
            for (ix,iy) in nbrs:
                if 0<=ix < b.shape[0] and 0<= iy < b.shape[1]:
                    if b[ix][iy] == 1:
                        n_count +=1

            return n_count
        moore_nb_vec = np.vectorize(moore_nb, excluded=[2])
        neighbor_matrix = np.fromfunction(lambda x,y: moore_nb_vec(x,y,self.board),shape=(10, 10), dtype=int)
        birth_condition = (neighbor_matrix == 3)
        survival_mask = (neighbor_matrix == 2) | (neighbor_matrix == 3)
        next_board = np.zeros_like(self.board)
        next_board[(self.board == 0) & birth_condition] = 1
        next_board[(self.board==1) & survival_mask] == 1
        self.board = next_board

def moore_nb(self,x,y,b):
        # Sequence goes top,a nd moves anti-clockwise
        n_count = 0
        nbrs  = [(x-1,y), (x-1,y-1),(x,y-1), (x+1,y-1),(x+1,y),(x+1,y+1),(x,y+1),(x-1,y+1)]
        for (ix,iy) in nbrs:
            if 0<=ix < b.shape[0] and 0<= iy < b.shape[1]:
                if b[ix][iy] == 1:
                    n_count +=1

        return n_count



def main():
    pass
    

    