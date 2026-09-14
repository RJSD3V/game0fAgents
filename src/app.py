import pygame
from pygame import surfarray

import sys
from numpy import *


pygame.init()

# Color palette

COLOR_BG= (0,0, 0)
COLOR_GRID = (200,200,200)
COLOR_CELL = (0, 180, 255)
COLOR_FOOD = ( 0, 255, 130)

WINDOW_WIDTH=2000
WINDOW_HEIGHT=2000


def drawGrid():
    blockSize = 25
    for x in range(0, WINDOW_WIDTH, blockSize):
        for y in range(0, WINDOW_HEIGHT, blockSize):
            rect = pygame.Rect(x, y, blockSize, blockSize)
            pygame.draw.rect(screen, COLOR_GRID, rect, 1)



def main():
    global screen, clock
    running = True
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("The Symbiosis Engine: Cellular Growth Matrix")
    clock = pygame.time.Clock()
    screen.fill(COLOR_BG)

    while running: 
        drawGrid()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


            pygame.display.flip()


        clock.tick(30)


if __name__ == '__main__':
    main()

