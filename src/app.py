import pygame
import sys



pygame.init()

# Color palette

COLOR_BG= (20,24, 30)
COLOR_GRID = (35,40,50)
COLOR_CELL = (0, 180, 255)
COLOR_FOOD = ( 0, 255, 130)

WINDOW_WIDTH=1050
WINDOW_HEIGHT=600

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("The Symbiosis Engine: Cellular Growth Matrix")
clock = pygame.time.Clock()


running = True
while running: 

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        screen.fill((20,24,30))

        pygame.draw.rect(screen, (0, 180, 255), [100,100, 50, 50])


        pygame.display.flip()


        clock.tick(30)





