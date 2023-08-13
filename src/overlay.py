import pygame
from settings import *


class Overlay:
    """
    Class that displays the overlay on the screen.
    """
    def __init__(self, player):
        self.display_surface = pygame.display.get_surface()  # Get the surface of the display (same as screen on main.py)
        self.player = player
        
        self.tools_surfaces = {tool:None for tool in player.tools}  # Getting the tools from the player
        self.seeds_surfaces = {seed:None for seed in player.seeds}  # Getting the seeds from the player
        self.import_assets()
        
    def import_assets(self):
        """
        Import the assets for the overlay from their respective spritesheets.
        """
        
        # Importing the tools ---------------------------------------------------------------------------
        basic_tools_materials = pygame.image.load('assets/Sprite sheets UI/Basic UI/Tools_ui.png').convert_alpha()
        frame_width = basic_tools_materials.get_width() // 3
        frame_height = basic_tools_materials.get_height() // 2
 
        for row in range(2):
            for col in range(3):
                # Get the frame from the spritesheet
                frame = basic_tools_materials.subsurface(pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height))
                if row == 0:
                    if col == 2 and 'water' in self.player.tools:
                        self.tools_surfaces['water'] = frame
                    if col == 1 and 'hoe' in self.player.tools:
                        self.tools_surfaces['hoe'] = frame
                if row == 1:
                    if col == 0 and 'axe' in self.player.tools:
                        self.tools_surfaces['axe'] = frame
                    
        # Importing the seeds ---------------------------------------------------------------------------
        basic_plants = pygame.image.load('assets/Objects/Basic Plants.png').convert_alpha()
        frame_width = basic_plants.get_width() // 6
        frame_height = basic_plants.get_height() // 2
        
        for row in range(2):
            for col in range(6):
                # Get the frame from the spritesheet
                frame = basic_plants.subsurface(pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height))
                if row == 0:
                    if col == 0 and 'corn' in self.player.seeds:
                        self.seeds_surfaces['corn'] = frame
                if row == 1:
                    if col == 0 and 'tomato' in self.player.seeds:
                        self.seeds_surfaces['tomato'] = frame
        
    def display(self):
        """
        Display the overlay on the screen.
        """
        tool_surface = self.tools_surfaces[self.player.selected_tool]
        tool_surface = pygame.transform.scale(tool_surface, (70, 70))
        tool_rect = tool_surface.get_rect(midbottom=OVERLAY_POS['tools'])
        self.display_surface.blit(tool_surface, tool_rect)
        
        seed_surface = self.seeds_surfaces[self.player.selected_seed]
        seed_surface = pygame.transform.scale(seed_surface, (50, 50))
        seed_rect = seed_surface.get_rect(midbottom=OVERLAY_POS['seeds'])
        self.display_surface.blit(seed_surface, seed_rect)