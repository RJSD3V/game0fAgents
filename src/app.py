import pygame
from pygame import surfarray
from board import Board, next_board

import sys
import numpy as np

pygame.init()
# Color palette

COLOR_BG= (0,0, 0)
COLOR_GRID = (200,200,200)
COLOR_CELL = (0, 180, 255)
COLOR_FOOD = ( 0, 255, 130)

CELL_SIZE = 10
board_rows = 60
board_cols = 80

cell_grid = Board.from_size(rows = board_rows, cols = board_cols)
WINDOW_WIDTH=board_cols * CELL_SIZE
WINDOW_HEIGHT=board_rows * CELL_SIZE


def draw_cells():
    """This loops over the cell grid and draws pixels on the screen based on if the cells are alive or dead."""
    for row in range(0, cell_grid.size['rows']):
        for col in range(0, cell_grid.size['cols']):
            if(cell_grid.is_alive(r=row,c=col)):
                rect = coordinate(row,col,CELL_SIZE)
                pygame.draw.rect(screen, COLOR_CELL, rect, 0)


def coordinate(row,col, CELL_SIZE) -> pygame.Rect:
    return pygame.Rect(col*CELL_SIZE,row*CELL_SIZE,CELL_SIZE,CELL_SIZE)


def main():
    global screen, clock
    running = True
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("The Symbiosis Engine: Cellular Growth Matrix")
    clock = pygame.time.Clock()
    
    cell_grid.seed_random(200)
    while running: 
        
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        cell_grid.step()
        screen.fill(COLOR_BG)
        draw_cells()
        pygame.display.flip()
        clock.tick(30)


if __name__ == '__main__':
    main()

