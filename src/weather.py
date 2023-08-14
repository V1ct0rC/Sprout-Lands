import pygame
from settings import *
from sprites import Tile

from random import randint, choice


class Day:
    """
    Class for the day/night cycle.
    """
    def __init__(self):
        self.display = pygame.display.get_surface()
        self.screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.day_color = [255, 255, 255]
        self.night_color = [40, 80, 115]
        
    def reset(self):
        self.day_color = [255, 255, 255]
        
    def update(self, dt):
        for i, color in enumerate(self.night_color):
            if self.day_color[i] > color:
                self.day_color[i] -= 2 * dt
                
        self.screen.fill(self.day_color)
        self.display.blit(self.screen, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

class Drop(Tile):
    """
    Class for rain drops. It can be used for rain particles or for puddles.
    """
    def __init__(self, surf, pos, moving, groups, z):
        super().__init__(pos, surf, groups, z)
        
        self.duration = randint(400, 500)
        self.time0 = pygame.time.get_ticks()
        
        self.moving = moving
        if self.moving:
            self.direction = pygame.math.Vector2(-2, 4)
            self.pos = pygame.math.Vector2(self.rect.topleft)
            self.speed = randint(50, 100)
            
    def update(self, dt):
        """
        Update the rain drop depending on its type.

        Args:
            dt (int): The time in milliseconds since the last frame.
        """
        if self.moving:  # If it is a drop
            self.pos += self.direction * self.speed * dt
            self.rect.topleft = ((round(self.pos.x)), (round(self.pos.y)))
            
        if pygame.time.get_ticks() - self.time0 >= self.duration:
            self.kill()

class Rain:
    """
    Class for rain particles and effects.
    """
    def __init__(self, all_sprites):
        self.all_sprites = all_sprites
        
        self.rain_drops = []
        self.rain_floor = []
        self.import_assets()
        
        self.floor_w , self.floor_h = MAP_WIDTH * TILE_SIZE, MAP_HEIGHT * TILE_SIZE
    
    def import_assets(self):
        """
        Import the rain assets.
        """
        
        # Each kind of rain drop has 3 different frames
        for i in range(1, 4):
            rain_frame = pygame.image.load(f"assets/Rain/rain{i}.png").convert_alpha()
            self.rain_drops.append(rain_frame)

            floor_rain_frame = pygame.image.load(f"assets/Rain/floor{i}.png").convert_alpha()
            self.rain_floor.append(floor_rain_frame)
            
    def create_puddle(self):
        """
        Create a rain drop on the floor (puddle).
        """
        Drop(surf=choice(self.rain_floor), 
             pos=(randint(0, self.floor_w), randint(0, self.floor_h)), 
             moving=False, 
             groups=self.all_sprites, 
             z=LAYERS['rain_floor'])
    
    def create_drop(self):
        """
        Create a falling rain drop.
        """
        Drop(surf=choice(self.rain_drops), 
             pos=(randint(0, self.floor_w), randint(0, self.floor_h)), 
             moving=True, 
             groups=self.all_sprites, 
             z=LAYERS['rain_drops'])
    
    def update(self):
        """
        Update the rain.
        """
        self.create_puddle() 
        self.create_drop()