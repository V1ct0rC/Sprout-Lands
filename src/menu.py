import pygame
from sprites import Water
from settings import *
from timer import Timer

from pytmx.util_pygame import load_pygame


class Buttons(pygame.sprite.Sprite):
    """
    TODO:
        Sprite Class for the buttons in the menu
    """
    def __init__(self, group):
        super().__init__(group, image, pos)
        self.image = image
        self.rect = self.image.get_rect(center=pos)

class Menu:
    """
    Class for the menu screen
    """
    def __init__(self):
        self.display_surface = pygame.display.get_surface()  # Get the surface of the display (same as screen on main.py)
        self.menu_sprites = pygame.sprite.Group()
        
        # Menu states -----------------------------------------------------------------------------------
        self.play = False
        self.config = False
        self.info = False
        
        self.state = "menu"
        self.timer = Timer(300)
        
        # Importing the assets --------------------------------------------------------------------------
        self.title_surface = pygame.image.load("assets/Title_tr.png").convert_alpha()
        self.title_rect = self.title_surface.get_rect(center=(SCREEN_WIDTH // 2, (SCREEN_HEIGHT // 2)-150))
        
        self.play_button_frames = []
        self.play_button_index = 0
        self.config_button_frames = []
        self.config_button_index = 0
        self.info_button_frames = []
        self.info_button_index = 0
        self.import_assets()
        
        # Creating the buttons --------------------------------------------------------------------------
        self.play_button_surface = self.play_button_frames[self.play_button_index]
        self.play_button_rect = self.play_button_surface.get_rect(center=((SCREEN_WIDTH // 2)-96, (SCREEN_HEIGHT // 2)+25))
        
        self.config_button_surface = self.config_button_frames[self.config_button_index]
        self.config_button_rect = self.config_button_surface.get_rect(center=((SCREEN_WIDTH // 2)+96, (SCREEN_HEIGHT // 2)+25))
        
        self.info_button_surface = self.info_button_frames[self.info_button_index]
        self.info_button_rect = self.info_button_surface.get_rect(center=((SCREEN_WIDTH // 2)+192, (SCREEN_HEIGHT // 2)+25))
        
    def import_assets(self):
        """
        Importing the assets for the menu screen. Each buttoon has two frames that comes from a sprite sheet with several buttons.
        The menu background is a tilemap.
        """
        
        # Importing the background water animation ------------------------------------------------------
        water_sprite = pygame.image.load("assets/Tilesets/Water.png").convert_alpha()
        frame_width = water_sprite.get_width() // 4
        frame_height = water_sprite.get_height() // 1
        
        water_frames = []
        for col in range(4):
            for row in range(1):
                frame = water_sprite.subsurface(pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height))
                frame = pygame.transform.scale(frame, (2*TILE_SIZE, 2*TILE_SIZE))
                water_frames.append(frame)
        
        for x, y, surface in load_pygame("data/tmx/map.tmx").get_layer_by_name("Water").tiles():     
            Water(pos=(x * TILE_SIZE * 2, y * TILE_SIZE * 2), frames=water_frames, groups=self.menu_sprites) 
                    
        # Importing the Play button ---------------------------------------------------------------------
        play_button_sheet = pygame.image.load("assets/Sprite sheets UI/Basic UI/UI Big Play Button.png").convert_alpha()
        frame_width = play_button_sheet.get_width() // 2
        frame_height = play_button_sheet.get_height() // 2
        
        for col in range(2):
            for row in range(2):
                frame = play_button_sheet.subsurface(pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height))
                frame = pygame.transform.scale(frame, (frame_width*3, frame_height*3))
                if row == 1:
                    self.play_button_frames.append(frame)
                    
        # Importing the Config and Info buttons ---------------------------------------------------------           
        config_button_sheet = pygame.image.load("assets/Sprite sheets UI/Basic UI/Config_btn.png").convert_alpha()
        info_button_sheet = pygame.image.load("assets/Sprite sheets UI/Basic UI/Info_btn.png").convert_alpha()
        frame_width = config_button_sheet.get_width() // 2
        frame_height = config_button_sheet.get_height() // 1
        
        for col in range(2):
            for row in range(1):
                frame = config_button_sheet.subsurface(pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height))
                frame = pygame.transform.scale(frame, (frame_width*3, frame_height*3))
                self.config_button_frames.append(frame)
                
                frame = info_button_sheet.subsurface(pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height))
                frame = pygame.transform.scale(frame, (frame_width*3, frame_height*3))
                self.info_button_frames.append(frame)
                    
    def menu_input(self):
        """
        Input for the menu screen. The buttons are activated and animated when the mouse is over them and the left button is pressed.
        """
        mouse = pygame.mouse.get_pos()
        if self.play_button_rect.collidepoint(mouse):
            if pygame.mouse.get_pressed()[0]:
                self.play_button_index = 1
                self.play_button_surface = self.play_button_frames[self.play_button_index]
                self.timer.activate()
                self.play = True
            else:
                self.play_button_index = 0
                self.play_button_surface = self.play_button_frames[self.play_button_index]
        
        if self.config_button_rect.collidepoint(mouse):
            if pygame.mouse.get_pressed()[0]:
                self.config_button_index = 1
                self.config_button_surface = self.config_button_frames[self.config_button_index]
                self.timer.activate()
                self.config = True
            else:
                self.config_button_index = 0
                self.config_button_surface = self.config_button_frames[self.config_button_index]
        
        if self.info_button_rect.collidepoint(mouse):
            if pygame.mouse.get_pressed()[0]:
                self.info_button_index = 1
                self.info_button_surface = self.info_button_frames[self.info_button_index]
                self.timer.activate()
                self.info = True
            else:
                self.info_button_index = 0
                self.info_button_surface = self.info_button_frames[self.info_button_index]
    
    def change_state(self):
        """
        Changing the state of the game according to the button pressed.
        """
        if self.play and not self.timer.active:
            self.play = False
            self.config = False
            self.info = False
            self.state = "level"
            
        if self.config and not self.timer.active:
            self.play = False
            self.config = False
            self.info = False
            self.state = "config"
            
        if self.info and not self.timer.active:
            self.play = False
            self.config = False
            self.info = False
            self.state = "info"
    
    def run(self, dt):
        """
        Running the menu screen.

        Args:
            dt (int): The time since the last frame.
        """
        self.display_surface.fill((0, 0, 0))
        self.menu_sprites.draw(self.display_surface)
        self.menu_sprites.update(dt)
        
        self.menu_input()
        self.timer.update()
        self.change_state()
        
        self.display_surface.blit(self.title_surface, self.title_rect)
        self.display_surface.blit(self.play_button_surface, self.play_button_rect)
        self.display_surface.blit(self.config_button_surface, self.config_button_rect)
        self.display_surface.blit(self.info_button_surface, self.info_button_rect)