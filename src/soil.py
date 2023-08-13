import pygame
from settings import *

from pytmx.util_pygame import load_pygame


class SoilTile(pygame.sprite.Sprite):
    """
    A class for farm tiles.
    """
    def __init__(self, pos, surf, groups, z = LAYERS["soil"]):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = z

class Soil:
    """
    A class for the soil in the farm.
    """
    def __init__(self, all_sprites):
        self.all_sprites = all_sprites
        self.soil_sprites = pygame.sprite.Group()
        self.soil_water_sprites = pygame.sprite.Group()
        
        self.soil_surface = None
        self.soil_water = None
        self.import_assets()
        self.create_scenario_grid()
        self.create_hittable_soil()
        
        self.raining = False
         
    def import_assets(self):
        """
        Importing the assets for the soil sprite sheet.
        """
        soil_tiles = pygame.image.load("assets/Tilesets/Tilled Dirt.png").convert_alpha()
        frame_width = soil_tiles.get_width() // 8
        frame_height = soil_tiles.get_height() // 8
        
        for col in range(8):
            for row in range(8):
                frame = soil_tiles.subsurface(pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height))
                if col == 2 and row == 4:
                    self.soil_surface = frame
                if col == 1 and row == 0:
                    self.soil_water = frame
                    
    def create_scenario_grid(self):
        """
        Create a grid with the scenario tiles. This grid will be used to manage the farm soil tiles.
        """
        self.grid = [[[] for col in range(MAP_WIDTH)] for row in range(MAP_HEIGHT)]
        for x, y, surface in load_pygame("data/tmx/map.tmx").get_layer_by_name("Farm Layer").tiles():
            self.grid[y][x].append("Farmable")
        
    def create_hittable_soil(self):
        """
        Create a list of Tiles that can be hit by the player's hoe to create farm tiles.
        """
        self.hittable_soil = []
        for y, row in enumerate(self.grid):
            for x, tile in enumerate(row):
                if "Farmable" in tile:
                    rect = pygame.Rect((x * TILE_SIZE), (y * TILE_SIZE), TILE_SIZE, TILE_SIZE)
                    self.hittable_soil.append(rect)
                
    def create_soil_tiles(self):
        """
        Create the soil tiles based on the scenario grid.
        """
        self.soil_sprites.empty()
        for y, row in enumerate(self.grid):
            for x, tile in enumerate(row):
                if "Soil" in tile:
                    SoilTile(((x * TILE_SIZE), (y * TILE_SIZE)), self.soil_surface, [self.all_sprites, self.soil_sprites])
    
    def hit(self, point):
        """
        Hit the soil with the hoe to create farm tiles.

        Args:
            point (Tuple[int, int]): The point where the player hit the soil.
        """
        for tile in self.hittable_soil:
            y = tile.y // TILE_SIZE
            x = tile.x // TILE_SIZE
            if tile.collidepoint(point) and "Farmable" in self.grid[y][x]:
                self.grid[y][x].append("Soil")
                self.create_soil_tiles()
                
                if self.raining:
                    self.water_all()
                
    def water(self, point):
        """
        Water the soil.

        Args:
            point (Tuple[int, int]): The point where the player watered the soil.
        """
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(point):
                x = soil_sprite.rect.x // TILE_SIZE
                y = soil_sprite.rect.y // TILE_SIZE
                self.grid[y][x].append("Watered")
                
                SoilTile(soil_sprite.rect.topleft, self.soil_water, [self.all_sprites, self.soil_water_sprites], LAYERS["soil_water"])
     
    def water_all(self):
        """
        Water all the soil tiles. It happens when it's raining.
        """
        for y, row in enumerate(self.grid):
            for x, tile in enumerate(row):
                if "Soil" in tile and "Watered" not in tile:
                    self.grid[y][x].append("Watered")
                    SoilTile(((x*TILE_SIZE),(y*TILE_SIZE)), self.soil_water, [self.all_sprites, self.soil_water_sprites], LAYERS["soil_water"])
                    
    def remove_water(self):
        """
        Remove the water from the soil tiles. Simulates the water evaporating over time.
        """
        for sprite in self.soil_water_sprites.sprites():
            sprite.kill()
            
        for y, row in enumerate(self.grid):
            for x, tile in enumerate(row):
                if "Watered" in tile:
                    self.grid[y][x].remove("Watered")
                    
        self.create_soil_tiles()
                