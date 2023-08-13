import pygame
from settings import *
from level import Level
from menu import Menu

import sys
from random import randint


class Game:
    """ 
    Main class of the game. It is responsible for the game loop and the game states.
    """
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock() 
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Sprout Lands")
        
        # Game states -----------------------------------------------------------------------------------
        self.state = "menu"
        self.menu = Menu()
        self.level = Level()
        
    def run(self):
        """
        Main game loop. It is responsible for the event management, game states and the delta time.
        """
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            # Using delta time to make the game be frame rate independent
            dt = self.clock.tick() / 1000  
            
            # Switching between game states (screens, scenes etc.)
            if self.menu.state == "level":
                self.state = "level"
            if self.state == "menu":
                self.menu.run(dt)
            if self.state == "level":
                self.level.run(dt)
                
            pygame.display.update()


if __name__ == '__main__':
    game = Game()
    game.run()