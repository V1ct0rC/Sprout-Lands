import os
import pygame


def import_assets_level(self):
    tmx_data = load_pygame("data/tmx/map.tmx")
    
    # Cycle through all the visible layers, and add them to the sprite group
    for layer in tmx_data.layers:
        # Ground layers
        if layer.name == "Ground":
            for x, y, surf in layer.tiles():
                Tile(pos=(x * TILE_SIZE, y * TILE_SIZE), surf=surf, groups=self.all_sprites, z=LAYERS["ground"])
        
        if layer.name == "Paths":
            for x, y, surf in layer.tiles():
                Tile(pos=(x * TILE_SIZE, y * TILE_SIZE), surf=surf, groups=self.all_sprites, z=LAYERS["ground_plants"])
    
        if layer.name == "Hills":
            for x, y, surf in layer.tiles():
                Tile(pos=(x * TILE_SIZE, y * TILE_SIZE), surf=surf, groups=self.all_sprites, z=LAYERS["ground_plants"])

        # House layers
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
                
        # Fences
        if layer.name == "Fences":
            for x, y, surf in layer.tiles():
                Tile(pos=(x * TILE_SIZE, y * TILE_SIZE), surf=surf, groups=[self.all_sprites, self.collision_sprites], z=LAYERS["main"])
                
        # Water
        water_sprite = pygame.image.load("assets/Tilesets/Water.png").convert_alpha()
        frame_width = water_sprite.get_width() // 4
        frame_height = water_sprite.get_height() // 1
        
        water_frames = []
        for col in range(4):
            for row in range(1):
                frame = water_sprite.subsurface(pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height))
                water_frames.append(frame)
        
        if layer.name == "Water":
            for x, y, surf in layer.tiles():
                Water(pos=(x * TILE_SIZE, y * TILE_SIZE), frames=water_frames, groups=self.all_sprites) 
        
        # Small plants (object layer)
        if layer.name == "Small Plants":
            for obj in layer:
                WildFlower(pos=(obj.x, obj.y), surf=obj.image, groups=[self.all_sprites, self.collision_sprites])
        
        if layer.name == "Hill Objects":
            for obj in layer:
                WildFlower(pos=(obj.x, obj.y), surf=obj.image, groups=[self.all_sprites, self.collision_sprites])
                
        # Trees (object layer)
        if layer.name == "Trees":
            for obj in layer:
                Tree(pos=(obj.x, obj.y), surf=obj.image, groups=[self.all_sprites, self.collision_sprites, self.tree_sprites], name=obj.name, update_inventory=self.update_inventory)
        
        # Player
        if layer.name == "Player":
            for obj in layer:
                if obj.name == "Spawn":
                    self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites, self.tree_sprites, self.interaction_sprites)
                if obj.name == "Bed":
                    Interaction(pos=(obj.x, obj.y), size=(obj.width, obj.height), groups=self.interaction_sprites, name=obj.name)
        
        # Collision layer
        if layer.name == "Collision Layer":
            for x, y, surf in layer.tiles():
                Tile(pos=(x * TILE_SIZE, y * TILE_SIZE), surf=pygame.Surface((TILE_SIZE, TILE_SIZE)), groups=self.collision_sprites, z=LAYERS["main"])
                
def import_assets_overlay(self):
    basic_tools_materials = pygame.image.load('assets/Objects/Basic tools and meterials.png').convert_alpha()
    frame_width = basic_tools_materials.get_width() // 3
    frame_height = basic_tools_materials.get_height() // 2

    for row in range(2):
        for col in range(3):
            # Get the frame from the spritesheet
            frame = basic_tools_materials.subsurface(pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height))
            if row == 0:
                if col == 0 and 'water' in self.player.tools:
                    self.tools_surfaces['water'] = frame
                if col == 1 and 'axe' in self.player.tools:
                    self.tools_surfaces['axe'] = frame
                if col == 2 and 'hoe' in self.player.tools:
                    self.tools_surfaces['hoe'] = frame
                
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
                
    
def import_assets_player(self):
    self.animations = {'up': [], 'down': [], 'left': [], 'right': [],
                        'up_idle': [], 'down_idle': [], 'left_idle': [], 'right_idle': [],
                        'up_hoe': [], 'down_hoe': [], 'left_hoe': [], 'right_hoe': [],
                        'up_axe': [], 'down_axe': [], 'left_axe': [], 'right_axe': [],
                        'up_water': [], 'down_water': [], 'left_water': [], 'right_water': []}
    
    basic_sprite_sheet = pygame.image.load('assets/Characters/Basic Charakter Spritesheet.png').convert_alpha()
    frame_width = basic_sprite_sheet.get_width() // 4
    frame_height = basic_sprite_sheet.get_height() // 4
    
    # This variable is used to store the frame of the animation and properly order them
    frame_1 = None
    frame_idle = None
    frame_2 = None
    frame_3 = None
    for row in range(4):
        for col in range(4):
            # Get the frame from the spritesheet
            frame = basic_sprite_sheet.subsurface(pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height))
            if col == 0:
                frame_1 = frame
            elif col == 1:
                frame_idle = frame
            elif col == 2:
                frame_2 = frame
            elif col == 3:
                frame_3 = frame
        
        # Setting the animation frame order        
        if row == 0:
            self.animations['down'] = [frame_1, frame_2, frame_1, frame_3]
            self.animations['down_idle'] = [frame_idle, frame_1]
        if row == 1:
            self.animations['up'] = [frame_1, frame_2, frame_1, frame_3]
            self.animations['up_idle'] = [frame_idle, frame_1]
        if row == 2:
            self.animations['left'] = [frame_1, frame_2, frame_1, frame_3]
            self.animations['left_idle'] = [frame_idle, frame_1]
        if row == 3:
            self.animations['right'] = [frame_1, frame_2, frame_1, frame_3]
            self.animations['right_idle'] = [frame_idle, frame_1]
                
    action_sprite_sheet = pygame.image.load('assets/Characters/Basic Charakter Actions.png').convert_alpha()
    frame_width = action_sprite_sheet.get_width() // 2
    frame_height = action_sprite_sheet.get_height() // 12
    
    for row in range(12):
        for col in range(2):
            # Get the frame from the spritesheet
            frame = action_sprite_sheet.subsurface(pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height))
            if row == 0:
                self.animations['down_hoe'].append(frame)
            elif row == 1:
                self.animations['up_hoe'].append(frame)
            elif row == 2:
                self.animations['left_hoe'].append(frame)
            elif row == 3:
                self.animations['right_hoe'].append(frame)
            
            if row == 4:
                self.animations['down_axe'].append(frame)
            elif row == 5:
                self.animations['up_axe'].append(frame)
            elif row == 6:
                self.animations['left_axe'].append(frame)
            elif row == 7:
                self.animations['right_axe'].append(frame)
                
            if row == 8:
                self.animations['down_water'].append(frame)
            elif row == 9:
                self.animations['up_water'].append(frame)
            elif row == 10:
                self.animations['left_water'].append(frame)
            elif row == 11:
                self.animations['right_water'].append(frame)
                
def import_assets_tree(self):
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