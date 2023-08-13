import pygame
from settings import *
from player import Player
from overlay import Overlay
from sprites import Tile, Water, WildFlower, Tree, Interaction
from soil import Soil
from weather import Rain

from pytmx.util_pygame import load_pygame
from random import randint


class Transition:
    """
    Class for the transition between days inside the level
    """
    def __init__(self, reset, player):
        self.reset = reset
        self.player = player
        self.display_surface = pygame.display.get_surface()
        
        # Transition variables --------------------------------------------------------------------------
        self.image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.color = 255
        self.speed = -2

    def play(self):
        """
        Play the transition when the player goes to sleep
        """
        self.color += self.speed
        if self.color <= 0:
            self.speed *= -1
            self.color = 0
            self.reset()
        if self.color >= 255:
            self.color = 255
            self.player.asleep = False
            self.speed = -2
            
        self.image.fill((self.color, self.color, self.color))
        self.display_surface.blit(self.image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

class Level:
    """
    Class for the level screen. This is where the player will play the game.
    """
    def __init__(self):
        self.display_surface = pygame.display.get_surface()  # Get the surface of the display (same as screen on main.py)
        
        # Sprite groups ---------------------------------------------------------------------------------
        self.all_sprites = CameraGroup()  # All sprites (everything)
        self.collision_sprites = pygame.sprite.Group()  # Only sprites that the player can collide with
        self.tree_sprites = pygame.sprite.Group()  # Only tree sprites
        self.interaction_sprites = pygame.sprite.Group()  # Only sprites that the player can interact with
        
        # Set up the player and its activities ----------------------------------------------------------
        self.player = None
        self.soil_layer = Soil(self.all_sprites)
        
        self.import_assets()  # Import all the assets from the tmx file
        
        # Set up the overlay and transition -------------------------------------------------------------
        self.overlay = Overlay(self.player)
        self.transition = Transition(self.reset, self.player)
        
        # Set up the weather ----------------------------------------------------------------------------
        self.rain = Rain(self.all_sprites)
        self.raining = (randint(0, 100) < 30)
        self.soil_layer.raining = self.raining
        
    def import_assets(self):
        """
        Import all map ans scenario related assets from a tmx file.
        """
        tmx_data = load_pygame("data/tmx/map.tmx")
        
        # Cycle through all the visible layers, and add them to the sprite group
        for layer in tmx_data.layers:
            # Ground layers -----------------------------------------------------------------------------
            if layer.name == "Ground":
                for x, y, surf in layer.tiles():
                    Tile(pos=(x * TILE_SIZE, y * TILE_SIZE), surf=surf, groups=self.all_sprites, z=LAYERS["ground"])
            
            if layer.name == "Paths":
                for x, y, surf in layer.tiles():
                    Tile(pos=(x * TILE_SIZE, y * TILE_SIZE), surf=surf, groups=self.all_sprites, z=LAYERS["ground_plants"])
        
            if layer.name == "Hills":
                for x, y, surf in layer.tiles():
                    Tile(pos=(x * TILE_SIZE, y * TILE_SIZE), surf=surf, groups=self.all_sprites, z=LAYERS["ground_plants"])

            # bulding layers ----------------------------------------------------------------------------
            if layer.name == "House Floor":
                for x, y, surf in layer.tiles():
                    Tile(pos=(x * TILE_SIZE, y * TILE_SIZE), surf=surf, groups=self.all_sprites, z=LAYERS["house_bottom"])
            if layer.name == "House Furniture Bottom":
                for x, y, surf in layer.tiles():
                    Tile(pos=(x * TILE_SIZE, y * TILE_SIZE), surf=surf, groups=self.all_sprites, z=LAYERS["house_bottom"])
            if layer.name == "House Walls":
                for x, y, surf in layer.tiles():
                    Tile(pos=(x * TILE_SIZE, y * TILE_SIZE), surf=surf, groups=self.all_sprites, z=LAYERS["main"])
            if layer.name == "House Furniture Top":
                for x, y, surf in layer.tiles():
                    Tile(pos=(x * TILE_SIZE, y * TILE_SIZE), surf=surf, groups=self.all_sprites, z=LAYERS["main"])
             
            if layer.name == "Fences":
                for x, y, surf in layer.tiles():
                    Tile(pos=(x * TILE_SIZE, y * TILE_SIZE), 
                         surf=surf, 
                         groups=[self.all_sprites, self.collision_sprites], 
                         z=LAYERS["main"])
                    
            # Water layers ------------------------------------------------------------------------------
            if layer.name == "Water":
                water_sprite = pygame.image.load("assets/Tilesets/Water.png").convert_alpha()
                frame_width = water_sprite.get_width() // 4
                frame_height = water_sprite.get_height() // 1
                
                water_frames = []
                for col in range(4):
                    for row in range(1):
                        frame = water_sprite.subsurface(pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height))
                        water_frames.append(frame)
                        
                for x, y, surf in layer.tiles():
                    Water(pos=(x * TILE_SIZE, y * TILE_SIZE), frames=water_frames, groups=self.all_sprites) 
            
            # Nature layers -----------------------------------------------------------------------------
            if layer.name == "Small Plants":
                for obj in layer:
                    WildFlower(pos=(obj.x, obj.y), surf=obj.image, groups=[self.all_sprites, self.collision_sprites])
            
            if layer.name == "Hill Objects":
                for obj in layer:
                    WildFlower(pos=(obj.x, obj.y), surf=obj.image, groups=[self.all_sprites, self.collision_sprites])
                    
            # Trees (object layer)
            if layer.name == "Trees":
                for obj in layer:
                    Tree(pos=(obj.x, obj.y), 
                         surf=obj.image, 
                         groups=[self.all_sprites, self.collision_sprites, self.tree_sprites], 
                         name=obj.name, 
                         update_inventory=self.update_inventory)
            
            # Player ------------------------------------------------------------------------------------
            if layer.name == "Player":
                for obj in layer:
                    if obj.name == "Spawn":
                        self.player = Player((obj.x, obj.y), 
                                             group=self.all_sprites, 
                                             collision_sprites=self.collision_sprites, 
                                             trees_sprites=self.tree_sprites, 
                                             interaction_sprites=self.interaction_sprites,
                                             soil_layer=self.soil_layer)
                    if obj.name == "Bed":
                        Interaction(pos=(obj.x, obj.y), size=(obj.width, obj.height), groups=self.interaction_sprites, name=obj.name)
            
            # Collision layer ---------------------------------------------------------------------------
            if layer.name == "Collision Layer":
                for x, y, surf in layer.tiles():
                    Tile(pos=(x * TILE_SIZE, y * TILE_SIZE), surf=pygame.Surface((TILE_SIZE, TILE_SIZE)), groups=self.collision_sprites, z=LAYERS["main"])      
    
    def update_inventory(self, item):
        """
        Update the player's inventory with the given item.

        Args:
            item (string): The name of the item (key) to add to the inventory
        """
        self.player.item_inventory[item] += 1;

    def reset(self):
        """
        Reset the game state when the player goes to sleep.
        """
        self.soil_layer.update_plants()
        self.soil_layer.remove_water()
        
        self.raining = (randint(0, 100) < 30)
        self.soil_layer.raining = self.raining
        
        if self.raining:
            self.soil_layer.water_all()
        
        for tree in self.tree_sprites.sprites():
            if tree.alive:
                for apple in tree.apple_sprites.sprites():
                    apple.kill()
                tree.create_fruit()
    
    def run(self, dt):
        """
        Run the level.

        Args:
            dt (int): The time since the last frame in milliseconds
        """
        self.display_surface.fill((0, 0, 0))
        self.all_sprites.custom_draw(self.player)
        # Calls update method on all sprites in the group
        self.all_sprites.update(dt)  
        self.overlay.display()
        
        if self.raining:
            self.rain.update()
        
        if self.player.asleep:
            self.transition.play()

class CameraGroup(pygame.sprite.Group):
    """
    A custom sprite group that handles drawing sprites with a camera offset and zoom applied.
    """
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2(0, 0)
        self.zoom = 3.0  # Default zoom level
        
    def custom_draw(self, player):
        """
        Draw the sprites in the group with the camera offset and zoom applied.

        Args:
            player (Player): The player object (the reference point for the camera)
        """
        # Calculate the scaled screen dimensions
        scaled_width = SCREEN_WIDTH // self.zoom
        scaled_height = SCREEN_HEIGHT // self.zoom
        
        self.offset.x = player.rect.centerx - scaled_width // 2
        self.offset.y = player.rect.centery - scaled_height // 2
        
        # Create a scaled surface for drawing sprites with the zoom applied
        scaled_surface = pygame.Surface((scaled_width, scaled_height))
        
        for layer in LAYERS.values():  # Cycle through all the layers
            # Sort sprites by y value, so they are drawn in the correct order relative to the player
            for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery): 
                if sprite.z == layer:  # Draw the sprite on the display surface according to its z value
                    # Apply the offset and zoom to the sprite
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    scaled_sprite_image = pygame.transform.scale(sprite.image, (int(sprite.rect.width), int(sprite.rect.height)))
                    scaled_surface.blit(scaled_sprite_image, offset_rect)
                    
                    # if sprite == player:
                    #     # Draw the player's hitbox and target position
                    #     pygame.draw.rect(scaled_surface, (255, 0, 0), offset_rect, 1)
                    #     hitbox_rect = player.hitbox.copy()
                    #     hitbox_rect.center = offset_rect.center
                    #     pygame.draw.rect(scaled_surface, (0, 255, 0), hitbox_rect, 1)
                    #     target_pos = offset_rect.center + PLAYER_TOOL_OFFSET[player.status.split('_')[0]]
                    #     pygame.draw.circle(scaled_surface, (0, 0, 255), target_pos, 2)

        # Scale the scaled_surface to fit the display surface
        zoomed_surface = pygame.transform.scale(scaled_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # Draw the zoomed surface on the display surface
        self.display_surface.blit(zoomed_surface, (0, 0))
        
    def custom_draw_no_zoom(self, player):
        # Player always stays in the center of the screen
        self.offset.x = player.rect.centerx - SCREEN_WIDTH // 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT // 2
        
        for layer in LAYERS.values():  # Cycle through all the layers
            # Sort sprites by y value, so they are drawn in the correct order relative to the player
            for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):  
                if sprite.z == layer:  # Draw the sprite on the display surface according to its z value
                    # Apply the offset to the sprite
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)
