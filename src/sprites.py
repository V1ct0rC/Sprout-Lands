import pygame
from settings import *
from timer import Timer

from random import randint, choice


class Tile(pygame.sprite.Sprite):
    """
    A class for tiles. Tiles are the base of the game, mos classes will end up inheriting from this one.
    """
    def __init__(self, pos, surf, groups, z=LAYERS["main"]):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(-self.rect.width * 0.3, -self.rect.height * 0.85)
        self.z = z
        
class Water(Tile):
    """
    A class for water tiles.
    """
    def __init__(self, pos, frames, groups):
        self.frames = frames
        self.frame_index = 0
        
        super().__init__(pos, self.frames[self.frame_index], groups, z=LAYERS["water"])
        
    def update(self, dt):
        """
        Update the water animation.

        Args:
            dt (int): The time in milliseconds since the last frame.
        """
        self.frame_index += 2 * dt 
        self.image = self.frames[int(self.frame_index) % len(self.frames)]
        
class WildFlower(Tile):
    """
    A class for small plants and nature structures.
    """
    def __init__(self, pos, surf, groups):
        super().__init__(pos, surf, groups, z=LAYERS["main"])
        self.hitbox = self.rect.inflate(-self.rect.width * 0.5, -self.rect.height * 0.95)
 
class Particle(Tile):
    """
    A class for particles. Particles are small objects that are created when something is destroyed.
    """
    def __init__(self, pos, surf, groups, z, duration=200):
        super().__init__(pos, surf, groups, z)
        self.time0 = pygame.time.get_ticks()
        self.duration = duration
        
        mask_surface = pygame.mask.from_surface(self.image)
        new_surface = mask_surface.to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
        self.image = new_surface
        
    def update(self, dt):
        """
        Update the particle sprite.

        Args:
            dt (int): The time in milliseconds since the last frame.
        """
        time = pygame.time.get_ticks()  # Get the current time in milliseconds
        if time - self.time0 > self.duration:
            self.kill()
        
class Tree(Tile):
    """
    A class for trees. Trees are the main source of wood and fruits in the game.
    """
    def __init__(self, pos, surf, groups, name, update_inventory):
        super().__init__(pos, surf, groups=groups, z=LAYERS["main"])
        self.hitbox = self.rect.inflate(-10, -self.rect.height * 0.95)
        
        self.groups = groups
        # I was not being able to access the groups attribute from the Sprite class groups()[i]
        
        # Status variables ------------------------------------------------------------------------------
        self.name = name
        self.health = 5
        self.alive = True 
        self.invulnerable_timer = Timer(200)
        
        # Importing the assets --------------------------------------------------------------------------
        self.stump_surface = None
        self.apple_surface = None
        self.apple_sprites = pygame.sprite.Group()
        self.import_assets()
        
        # Apple creation --------------------------------------------------------------------------------
        self.apple_pos = APPLE_POS[name]  # The position of the apples in the tree
        self.create_fruit()
        
        # Drop management -------------------------------------------------------------------------------
        self.update_inventory = update_inventory
        
    def import_assets(self):
        """
        Import the assets for the tree from the spritesheet.
        """
        grass_biom_sprites = pygame.image.load("assets/Objects/Basic Grass Biom things 1.png").convert_alpha()
        frame_width = grass_biom_sprites.get_width() // 9
        frame_height = grass_biom_sprites.get_height() // 5
        
        for col in range(9):
            for row in range(5):
                frame = grass_biom_sprites.subsurface(pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height))
                if col == 0 and row == 2:
                    self.apple_surface = frame
                
                if self.name == "Tree":
                    if col == 3 and row == 2:
                        self.stump_surface = frame
                
                if self.name == "Tree Large":
                    if col == 4 and row == 2:
                        self.stump_surface = frame
                    
    def create_fruit(self):
        """
        Create the apples in the tree. For each position in the apple_pos list, there is a 30% chance of creating an apple.
        """
        for pos in self.apple_pos:
            if randint(0, 10) < 3:
                x = self.rect.left + pos[0]
                y = self.rect.top + pos[1]
                
                # Apples do not need an specific class
                Tile(pos=(x, y), 
                     surf=self.apple_surface, 
                     groups=[self.apple_sprites, self.groups[0]], 
                     z=LAYERS["fruits"])
                
    def damage(self):
        """
        Damage the tree. If the tree has no more health, it dies. Each hit drops an apple (if there are apples).
        """
        self.health -= 1
        
        if len(self.apple_sprites.sprites()) > 0:
            random_apple = choice(self.apple_sprites.sprites())
            random_apple.kill()
            
            # Create a particle for the removed apple
            Particle(random_apple.rect.topleft, 
                     random_apple.image, 
                     groups=[self.groups[0]], 
                     z=LAYERS["fruits"])
            self.update_inventory('apple')
            
    def death(self):
        """
        Kills the tree. If the tree is dead, it drops wood and creates a stump.
        """
        if self.health <= 0:
            Particle(self.rect.topleft, 
                     self.image, 
                     groups=[self.groups[0]], 
                     z=LAYERS["fruits"])
            
            # Create a stump
            self.image = self.stump_surface
            self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
            self.hitbox = self.rect.inflate(-10, -self.rect.height * 0.6)
            self.alive = False
            
            # Drop wood
            self.update_inventory('wood')
        
    def update(self, dt):
        """
        Update the tree sprite.

        Args:
            dt (int): The time in milliseconds since the last frame.
        """
        if self.alive:
            self.death()

class Interaction(Tile):
    """
    A class for interaction tiles. Interaction tiles are tiles that can be interacted with by the player.
    """
    def __init__(self, pos, size, groups, name):
        surf = pygame.Surface(size)
        super().__init__(pos, surf, groups, z=LAYERS["main"])
        
        self.name = name
