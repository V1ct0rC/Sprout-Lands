import pygame, sys
from settings import *
from timer import Timer


class Player(pygame.sprite.Sprite):
    """
    Class for the player object. A player object can move, use tools and seeds, and interact with other objects.
    """
    def __init__(self, pos, group, collision_sprites, trees_sprites, interaction_sprites, soil_layer):
        super().__init__(group)  # The object will be added to the group
        
        # Image and animation ---------------------------------------------------------------------------
        self.animations = {}
        self.import_assets()
        self.status = "down_idle"
        self.frame_index = 0
        
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center = pos)
        self.z = LAYERS['main']
        
        # Movement --------------------------------------------------------------------------------------
        self.direction = pygame.math.Vector2(0, 0)
        
        # pos can store floats (differently from rect.x and rect.y)
        self.pos = pygame.math.Vector2(self.rect.center)  
        self.speed = 50
        
        # Timers ----------------------------------------------------------------------------------------
        self.timers = {'tool_use': Timer(350, self.use_tool),
                       'seed_use': Timer(350, self.use_seed),
                       'seed_change': Timer(200)}
        
        # Tools and seeds -------------------------------------------------------------------------------
        self.tools = ['hoe', 'axe', 'water']
        self.tools_index = 0
        self.selected_tool = self.tools[self.tools_index]
        
        self.seeds = ['tomato', 'corn']
        self.seeds_index = 0
        self.selected_seed = self.seeds[self.seeds_index]
        
        # Collision -------------------------------------------------------------------------------------
        self.hitbox = self.rect.copy().inflate(-35, -30)  # The hitbox is smaller than the actual image
        self.collision_sprites = collision_sprites
        
        # Inventory and itens ---------------------------------------------------------------------------
        self.tree_sprites = trees_sprites
        self.target_pos = self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]
        self.item_inventory = {'tomato': 0, 'corn': 0, 'apple': 0, 'wood': 0}
        
        # Interaction -----------------------------------------------------------------------------------
        self.interaction_sprites = interaction_sprites
        self.asleep = False
        self.soil_layer = soil_layer
        
    def import_assets(self):
        """
        Import the assets for the player and store them in the animations dictionary according to their status.
        """
        self.animations = {'up': [], 'down': [], 'left': [], 'right': [],
                           'up_idle': [], 'down_idle': [], 'left_idle': [], 'right_idle': [],
                           'up_hoe': [], 'down_hoe': [], 'left_hoe': [], 'right_hoe': [],
                           'up_axe': [], 'down_axe': [], 'left_axe': [], 'right_axe': [],
                           'up_water': [], 'down_water': [], 'left_water': [], 'right_water': []}
        
        # Importing player's moviment animations --------------------------------------------------------
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
                    
        # Importing player's actions animations ---------------------------------------------------------
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
        
    def player_input(self):
        keys = pygame.key.get_pressed()
        
        if not self.timers['tool_use'].active and not self.asleep:  # The player can not move while using a tool
            # Directions --------------------------------------------------------------------------------
            self.movement = "stand"
            # Get the direction of the player (vertical and horizontal axis)
            self.direction.y = 0  # Default y value
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.status = "up"
                self.direction.y = -1
            elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.status = "down"
                self.direction.y = 1
                
            self.direction.x = 0  # Default x value
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:   
                self.status = "left"
                self.direction.x = -1
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.status = "right"
                self.direction.x = 1
                
            # Tools -------------------------------------------------------------------------------------
            if keys[pygame.K_SPACE] :
                self.timers['tool_use'].activate()
                self.direction = pygame.math.Vector2(0, 0)  # Reset the direction so that the player can't move while using a tool
                self.frame_index = 0
            
            # Change the selected tool
            if keys[pygame.K_1]:
                self.tools_index = 0
                self.selected_tool = self.tools[self.tools_index]
            elif keys[pygame.K_2]:
                self.tools_index = 1
                self.selected_tool = self.tools[self.tools_index]
            elif keys[pygame.K_3]:
                self.tools_index = 2
                self.selected_tool = self.tools[self.tools_index]
                
            # Seeds -------------------------------------------------------------------------------------
            if keys[pygame.K_e]:
                self.timers['seed_use'].activate()
                self.direction = pygame.math.Vector2(0, 0)
                self.frame_index = 0
                #print("Seed used")
                
            # Change the selected seed
            if keys[pygame.K_c] and not self.timers['seed_change'].active:
                self.timers['seed_change'].activate()
                self.seeds_index += 1
                self.selected_seed = self.seeds[self.seeds_index % len(self.seeds)]
                #print(self.selected_seed)
                
            # Interact ----------------------------------------------------------------------------------
            if keys[pygame.K_RETURN]:
                collided_sprite = pygame.sprite.spritecollide(self, self.interaction_sprites, False)
                if collided_sprite and collided_sprite[0].name == "Bed":
                    if collided_sprite[0].rect.bottom >= self.rect.centery:
                        self.status = "left_idle"
                    else: 
                        self.status = "up_idle"  
                    self.asleep = True            
        
    def use_tool(self):
        """
        Use the selected tool on the target position
        """
        if self.selected_tool == "hoe":
            self.soil_layer.hit(self.target_pos)
            
        if self.selected_tool == "axe":
            for tree in self.tree_sprites.sprites():
                if tree.rect.collidepoint(self.target_pos):
                    tree.damage()
                    
        if self.selected_tool == "water":
            self.soil_layer.water(self.target_pos)
        
    def use_seed(self):
        self.soil_layer.plant(self.target_pos, self.selected_seed)
    
    def set_status(self):
        """
        Set the status of the player depending on the direction and the selected tool
        """
        # Idle status
        if self.direction.x == 0 and self.direction.y == 0:
            self.status = self.status.split("_")[0] + "_idle"
        
        # Tool status
        if self.timers['tool_use'].active:
            self.status = self.status.split("_")[0] + "_" + self.selected_tool
            
    def move(self, dt):
        """
        Move the player in the direction of the vector self.direction

        Args:
            dt (int): Time since the last frame
        """
        if self.direction.x != 0 and self.direction.y != 0:
            self.direction = self.direction.normalize()  # Normalize the vector so that the player can't move faster diagonally
        
        # Splitting in two axis to help with collision detection
        self.pos.x += self.direction.x * self.speed * dt  # Horizontal axis
        self.hitbox.centerx = round(self.pos.x)  # Round the position to avoid truncating the value
        self.rect.centerx = round(self.pos.x)
        self.collide('x')
        
        self.pos.y += self.direction.y * self.speed * dt  # Vertical axis
        self.hitbox.centery = round(self.pos.y)  # Round the position to avoid truncating the value
        self.rect.centery = round(self.pos.y)
        self.collide('y')
          
    def animate(self, dt):
        """
        Animate the player

        Args:
            dt (int): Time since the last frame
        """
        self.frame_index += dt * 4
        self.image = self.animations[self.status][int(self.frame_index) % len(self.animations[self.status])]
    
    def collide(self, direction):
        """
        Check if the player is colliding with an obstacle and move him accordingly

        Args:
            direction (string): The axis on which the player is moving
        """
        for sprite in self.collision_sprites.sprites():
            if hasattr(sprite, 'hitbox'):
                if self.hitbox.colliderect(sprite.hitbox):
                    if direction == 'x':  # If the player is moving on the x axis
                        if self.direction.x > 0:  # If the player is moving right
                            self.hitbox.right = sprite.hitbox.left
                        if self.direction.x < 0:  # If the player is moving left
                            self.hitbox.left = sprite.hitbox.right
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx
                        
                    if direction == 'y':  # If the player is moving on the y axis
                        if self.direction.y > 0:  # If the player is moving down
                            self.hitbox.bottom = sprite.hitbox.top
                        if self.direction.y < 0:  # If the player is moving up
                            self.hitbox.top = sprite.hitbox.bottom
                        self.rect.centery = self.hitbox.centery   
                        self.pos.y = self.rect.centery
    
    def update(self, dt):
        """
        Update the player atritbutes.

        Args:
            dt (int): Time since the last frame
        """
        self.player_input()
        self.set_status()
        
        for timer in self.timers.values():
            timer.update()
        self.target_pos = self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]
        
        self.move(dt)
        self.animate(dt)
