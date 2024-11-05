import pygame
import random
import math
import os
from pygame.transform import scale, flip

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Add to the constants section
LEVEL_1_SPEED = 1  # Slower enemies
LEVEL_2_SPEED = 2  # Normal speed
LEVEL_3_SPEED = 3  # Faster enemies
LEVEL_1_ENEMIES = 25
LEVEL_2_ENEMIES = 50
LEVEL_3_ENEMIES = 100
ARC_PROJECTILE_COUNT = 5  # Number of projectiles in the arc
ARC_SPREAD = 60  # Spread angle in degrees
BURST_COUNT = 3  # Number of bursts
BURST_DELAY = 100  # Milliseconds between bursts

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, speed=10):
        super().__init__()
        # Load and scale the bullet image
        self.original_image = pygame.image.load(os.path.join('assets', 'bullet.png'))
        scale_factor = 0.2  # Keep visual size small
        self.original_image = scale(self.original_image, 
                                  (int(self.original_image.get_width() * scale_factor),
                                   int(self.original_image.get_height() * scale_factor)))
        
        # Rotate image to match direction
        angle = math.degrees(math.atan2(-direction[1], direction[0]))
        self.image = pygame.transform.rotate(self.original_image, angle)
        
        # Create rect and make hitbox bigger than visual
        self.rect = self.image.get_rect()
        self.rect.width *= 2  # Double the width of hitbox
        self.rect.height *= 2  # Double the height of hitbox
        
        # Center the larger hitbox on the bullet
        self.rect.center = (x, y)
        
        self.direction = direction
        self.speed = speed
        self.lifetime = 500  # milliseconds
        self.spawn_time = pygame.time.get_ticks()

    def update(self):
        # Move in the specified direction
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed
        
        # Delete if lifetime is over
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()

class SingAttack(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        # Create a circular attack instead of using image
        self.radius = 50  # Starting radius
        self.max_radius = 200  # Maximum radius
        self.growth_speed = 5  # How fast the circle expands
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.player = player
        self.alpha = 255  # Start fully opaque
        self.draw_circle()

    def draw_circle(self):
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        # Draw purple circle with transparency
        pygame.draw.circle(self.image, (147, 0, 211, self.alpha), 
                         (self.radius, self.radius), self.radius, 3)
        self.rect = self.image.get_rect(center=self.player.rect.center)

    def update(self):
        # Expand the radius
        self.radius += self.growth_speed
        # Fade out as it expands
        self.alpha = max(0, 255 * (1 - self.radius / self.max_radius))
        
        # Update the circle
        self.draw_circle()
        
        # Keep centered on player
        self.rect.center = self.player.rect.center
        
        # Kill when reached max size
        if self.radius >= self.max_radius:
            self.kill()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Define scale factor first
        scale_factor = 1
        
        # Load sprite sheets
        self.walk_sheet = pygame.image.load(os.path.join('assets', 'Soldier_1', 'Walk.png'))
        self.shot_sheet = pygame.image.load(os.path.join('assets', 'Soldier_1', 'Shot_1.png'))
        self.hurt_sheet = pygame.image.load(os.path.join('assets', 'Soldier_1', 'Hurt.png'))
        
        # Define frame dimensions for hurt animation
        hurt_frame_width = self.hurt_sheet.get_width() // 3  # 3 frames for hurt
        hurt_frame_height = self.hurt_sheet.get_height()
        
        # Create hurt frames
        self.hurt_frames_right = []
        self.hurt_frames_left = []
        
        # Extract and scale hurt frames
        for i in range(3):  # 3 frames for hurt animation
            frame = pygame.Surface((hurt_frame_width, hurt_frame_height), pygame.SRCALPHA)
            frame.blit(self.hurt_sheet, (0, 0), (i * hurt_frame_width, 0, hurt_frame_width, hurt_frame_height))
            scaled_frame = scale(frame, 
                               (int(hurt_frame_width * scale_factor),
                                int(hurt_frame_height * scale_factor)))
            self.hurt_frames_right.append(scaled_frame)
            self.hurt_frames_left.append(flip(scaled_frame, True, False))
        
        # Extract shot frames
        self.shot_frames_right = []
        self.shot_frames_left = []
        
        # Define shot frame dimensions
        shot_frame_width = self.shot_sheet.get_width() // 4  # 4 frames in shot sheet
        shot_frame_height = self.shot_sheet.get_height()
        
        # Scale factor
        scale_factor = 1
        
        # Extract and scale shot frames
        for i in range(4):  # 4 frames for shooting
            # Extract frame
            frame = pygame.Surface((shot_frame_width, shot_frame_height), pygame.SRCALPHA)
            frame.blit(self.shot_sheet, (0, 0), (i * shot_frame_width, 0, shot_frame_width, shot_frame_height))
            # Scale frame
            scaled_frame = scale(frame, 
                               (int(shot_frame_width * scale_factor),
                                int(shot_frame_height * scale_factor)))
            
            # Store right-facing frame
            self.shot_frames_right.append(scaled_frame)
            # Store left-facing frame
            self.shot_frames_left.append(flip(scaled_frame, True, False))
        
        # Load sprite sheets
        self.walk_sheet = pygame.image.load(os.path.join('assets', 'Soldier_1', 'Walk.png'))
        self.shot_image = pygame.image.load(os.path.join('assets', 'Soldier_1', 'Shot_1.png'))
        
        # Scale shot image
        scale_factor = 1
        self.shot_image = scale(self.shot_image, 
                              (int(self.shot_image.get_width() * scale_factor),
                               int(self.shot_image.get_height() * scale_factor)))
        self.shot_image_left = flip(self.shot_image, True, False)
        
        # Define frame dimensions
        frame_width = self.walk_sheet.get_width() // 7  # 7 frames in the sheet
        frame_height = self.walk_sheet.get_height()
        
        scale_factor = 1  
        
        # Create two sets of frames: right-facing and left-facing
        self.walk_frames_right = []
        self.walk_frames_left = []
        
        for i in range(7):  # 7 frames
            # Extract frame
            frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            frame.blit(self.walk_sheet, (0, 0), (i * frame_width, 0, frame_width, frame_height))
            # Scale frame
            scaled_frame = scale(frame, 
                               (int(frame_width * scale_factor),
                                int(frame_height * scale_factor)))
            
            # Store right-facing frame
            self.walk_frames_right.append(scaled_frame)
            # Store left-facing frame (flipped)
            self.walk_frames_left.append(flip(scaled_frame, True, False))
        
        # Animation variables
        self.current_frame = 0
        self.animation_speed = 0.2
        self.animation_timer = 0
        
        # Set initial image and rect
        self.image = self.walk_frames_right[0]
        self.rect = self.image.get_rect()
        
        # Create a collision box with half width
        self.rect.width = self.rect.width // 8
        self.rect.height = self.rect.height // 8
        
        # Center the collision box
        self.rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        
        # Offset the sprite drawing position
        self.sprite_offset_x = -40  # Adjust these values to move the sprite
        self.sprite_offset_y = -80  # Negative values move up/left
        
        # Movement attributes
        self.speed = 3  # Changed from 5 to 3 for slower movement
        self.facing_left = False
        
        # Other attributes
        self.experience = 0
        self.level = 1
        self.health = 100
        self.max_health = 100
        self.last_direction = (1, 0)
        self.sing_cooldown = 2000
        self.last_sing = 0

        self.is_shooting = False
        self.shot_duration = 200  # How long to show shot animation (milliseconds)
        self.shot_timer = 0

        # Add shooting animation variables
        self.shot_frame = 0
        self.shot_animation_speed = 0.3  # Adjust for faster/slower animation
        self.shot_animation_timer = 0

        # Add hurt animation variables
        self.is_hurt = False
        self.hurt_frame = 0
        self.hurt_animation_speed = 0.2
        self.hurt_animation_timer = 0
        self.hurt_duration = 500  # milliseconds
        self.hurt_start_time = 0
        self.invulnerable = False
        self.invulnerable_duration = 1000  # 1 second of invulnerability after getting hurt

        # Add hurt effect variables
        self.hurt_flash = False
        self.flash_duration = 100  # milliseconds for each flash
        self.flash_count = 3  # number of flashes
        self.current_flash = 0
        self.last_flash = 0

        # Load recharge animation
        self.recharge_sheet = pygame.image.load(os.path.join('assets', 'Soldier_1', 'Recharge.png'))
        recharge_frame_width = self.recharge_sheet.get_width() // 13  # 13 frames
        recharge_frame_height = self.recharge_sheet.get_height()
        
        # Create recharge frames
        self.recharge_frames_right = []
        self.recharge_frames_left = []
        
        for i in range(13):  # 13 frames for recharge animation
            frame = pygame.Surface((recharge_frame_width, recharge_frame_height), pygame.SRCALPHA)
            frame.blit(self.recharge_sheet, (0, 0), 
                      (i * recharge_frame_width, 0, recharge_frame_width, recharge_frame_height))
            scaled_frame = scale(frame, 
                               (int(recharge_frame_width * scale_factor),
                                int(recharge_frame_height * scale_factor)))
            self.recharge_frames_right.append(scaled_frame)
            self.recharge_frames_left.append(flip(scaled_frame, True, False))
        
        # Add recharge animation variables
        self.recharge_frame = 0
        self.recharge_animation_speed = 0.2
        self.recharge_animation_timer = 0

        # Add ammo variables
        self.max_ammo = 10
        self.current_ammo = self.max_ammo
        self.is_recharging = False
        self.recharge_duration = 1000  # 1 second to recharge
        self.recharge_start_time = 0

        # Load death animation
        self.death_sheet = pygame.image.load(os.path.join('assets', 'Soldier_1', 'Dead.png'))
        death_frame_width = self.death_sheet.get_width() // 4  # 4 frames for death
        death_frame_height = self.death_sheet.get_height()
        
        # Create death frames
        self.death_frames_right = []
        self.death_frames_left = []
        
        for i in range(4):  # 4 frames for death animation
            frame = pygame.Surface((death_frame_width, death_frame_height), pygame.SRCALPHA)
            frame.blit(self.death_sheet, (0, 0), 
                      (i * death_frame_width, 0, death_frame_width, death_frame_height))
            scaled_frame = scale(frame, 
                               (int(death_frame_width * scale_factor),
                                int(death_frame_height * scale_factor)))
            self.death_frames_right.append(scaled_frame)
            self.death_frames_left.append(flip(scaled_frame, True, False))
        
        # Add death animation variables
        self.is_dead = False
        self.death_frame = 0
        self.death_animation_speed = 0.15
        self.death_animation_timer = 0
        self.death_start_time = 0
        self.death_duration = 2000  # 2 seconds

    def take_damage(self):
        if not self.invulnerable:
            self.is_hurt = True
            self.hurt_frame = 0
            self.hurt_animation_timer = 0
            self.hurt_start_time = pygame.time.get_ticks()
            self.invulnerable = True
            # Initialize flash effect
            self.hurt_flash = True
            self.current_flash = 0
            self.last_flash = pygame.time.get_ticks()

    def update(self):
        current_time = pygame.time.get_ticks()
        
        # Handle death animation
        if self.is_dead:
            self.death_animation_timer += self.death_animation_speed
            if self.death_animation_timer >= 1:
                self.death_animation_timer = 0
                if self.death_frame < len(self.death_frames_right) - 1:
                    self.death_frame += 1
                
            # Use death animation frames
            if self.facing_left:
                self.image = self.death_frames_left[self.death_frame]
            else:
                self.image = self.death_frames_right[self.death_frame]
            return  # Skip other animations when dead
        
        # Handle flash effect
        if self.hurt_flash:
            if current_time - self.last_flash > self.flash_duration:
                self.current_flash += 1
                self.hurt_flash = self.current_flash < self.flash_count * 2  # *2 for on/off cycles
                self.last_flash = current_time

        # Check if invulnerability should end
        if self.invulnerable and current_time - self.hurt_start_time > self.invulnerable_duration:
            self.invulnerable = False
        
        # Update hurt animation
        if self.is_hurt:
            self.hurt_animation_timer += self.hurt_animation_speed
            if self.hurt_animation_timer >= 1:
                self.hurt_animation_timer = 0
                self.hurt_frame += 1
                if self.hurt_frame >= len(self.hurt_frames_right):
                    self.hurt_frame = 0
                    self.is_hurt = False
            
            # Use hurt animation frames
            if self.facing_left:
                self.image = self.hurt_frames_left[self.hurt_frame]
            else:
                self.image = self.hurt_frames_right[self.hurt_frame]
            
            # Skip rest of update if hurt
            return

        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        moving = False
        
        # Check for shooting
        if keys[pygame.K_SPACE]:
            self.is_shooting = True
            
        # Update shooting animation
        if self.is_shooting:
            self.shot_animation_timer += self.shot_animation_speed
            if self.shot_animation_timer >= 1:
                self.shot_animation_timer = 0
                self.shot_frame += 1
                if self.shot_frame >= len(self.shot_frames_right):
                    self.shot_frame = 0
                    self.is_shooting = False
        
        # Movement keys
        if keys[pygame.K_w]:
            dy -= self.speed
            moving = True
        if keys[pygame.K_s]:
            dy += self.speed
            moving = True
        if keys[pygame.K_a]:
            dx -= self.speed
            moving = True
            self.facing_left = True
        if keys[pygame.K_d]:
            dx += self.speed
            moving = True
            self.facing_left = False

        # Update position
        self.rect.x += dx
        self.rect.y += dy

        # Update animation
        if self.is_shooting:
            # Use current shot frame
            if self.facing_left:
                self.image = self.shot_frames_left[self.shot_frame]
            else:
                self.image = self.shot_frames_right[self.shot_frame]
        elif moving:
            # Walking animation
            self.animation_timer += self.animation_speed
            if self.animation_timer >= 1:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.walk_frames_right)
                if self.facing_left:
                    self.image = self.walk_frames_left[self.current_frame]
                else:
                    self.image = self.walk_frames_right[self.current_frame]
        else:
            # Idle animation
            self.current_frame = 0
            if self.facing_left:
                self.image = self.walk_frames_left[0]
            else:
                self.image = self.walk_frames_right[0]

        # Update last direction if moving
        if dx != 0 or dy != 0:
            total = math.sqrt(dx*dx + dy*dy)
            self.last_direction = (dx/total if total != 0 else 0, 
                                 dy/total if total != 0 else 0)

        # Keep player on screen
        self.rect.clamp_ip(pygame.display.get_surface().get_rect())

        # Handle recharging
        if self.is_recharging:
            # Update recharge animation
            self.recharge_animation_timer += self.recharge_animation_speed
            if self.recharge_animation_timer >= 1:
                self.recharge_animation_timer = 0
                self.recharge_frame = (self.recharge_frame + 1) % len(self.recharge_frames_right)
                
            # Use recharge animation frames
            if self.facing_left:
                self.image = self.recharge_frames_left[self.recharge_frame]
            else:
                self.image = self.recharge_frames_right[self.recharge_frame]
            
            # Check if recharge is complete
            if current_time - self.recharge_start_time >= self.recharge_duration:
                self.is_recharging = False
                self.current_ammo = self.max_ammo
                self.recharge_frame = 0
            return  # Skip other animations while recharging

    def sing_attack(self, game):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_sing >= self.sing_cooldown:
            sing = SingAttack(self)
            game.all_sprites.add(sing)
            game.sing_attacks.add(sing)
            self.last_sing = current_time

    def draw(self, surface):
        # Create a copy of the current image for tinting
        current_image = self.image.copy()
        
        # If flashing and on a flash cycle, tint the image red
        if self.hurt_flash and (self.current_flash % 2 == 0):
            # Create a red overlay
            red_overlay = pygame.Surface(current_image.get_size()).convert_alpha()
            red_overlay.fill((255, 0, 0, 128))  # Semi-transparent red
            current_image.blit(red_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        # Draw the sprite at an offset from the collision box
        sprite_pos = (self.rect.x + self.sprite_offset_x, 
                     self.rect.y + self.sprite_offset_y)
        surface.blit(current_image, sprite_pos)

    def shoot(self):
        if self.current_ammo > 0:
            self.current_ammo -= 1
            if self.current_ammo <= 0:
                self.is_recharging = True
                self.recharge_start_time = pygame.time.get_ticks()
            return True
        return False

    def die(self):
        if not self.is_dead:
            self.is_dead = True
            self.death_frame = 0
            self.death_animation_timer = 0
            self.death_start_time = pygame.time.get_ticks()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, player, level):
        super().__init__()
        # Load sprite sheets
        self.walk_sheet = pygame.image.load(os.path.join('assets', 'Zombie Man', 'Walk.png'))
        self.attack_sheet = pygame.image.load(os.path.join('assets', 'Zombie Man', 'Attack_1.png'))
        
        # Define frame dimensions
        self.walk_frame_width = self.walk_sheet.get_width() // 8
        self.walk_frame_height = self.walk_sheet.get_height()
        self.attack_frame_width = self.attack_sheet.get_width() // 5  # 5 frames for attack
        self.attack_frame_height = self.attack_sheet.get_height()
        
        # Scale factor
        scale_factor = 1
        
        # Create walk frames
        self.walk_frames_right = []
        self.walk_frames_left = []
        
        for i in range(8):
            frame = pygame.Surface((self.walk_frame_width, self.walk_frame_height), pygame.SRCALPHA)
            frame.blit(self.walk_sheet, (0, 0), (i * self.walk_frame_width, 0, self.walk_frame_width, self.walk_frame_height))
            scaled_frame = scale(frame, 
                               (int(self.walk_frame_width * scale_factor),
                                int(self.walk_frame_height * scale_factor)))
            self.walk_frames_right.append(scaled_frame)
            self.walk_frames_left.append(flip(scaled_frame, True, False))
        
        # Create attack frames
        self.attack_frames_right = []
        self.attack_frames_left = []
        
        for i in range(5):  # 5 frames for attack animation
            frame = pygame.Surface((self.attack_frame_width, self.attack_frame_height), pygame.SRCALPHA)
            frame.blit(self.attack_sheet, (0, 0), (i * self.attack_frame_width, 0, self.attack_frame_width, self.attack_frame_height))
            scaled_frame = scale(frame, 
                               (int(self.attack_frame_width * scale_factor),
                                int(self.attack_frame_height * scale_factor)))
            self.attack_frames_right.append(scaled_frame)
            self.attack_frames_left.append(flip(scaled_frame, True, False))
        
        # Set initial image and create rect
        self.image = self.walk_frames_right[0]
        self.rect = self.image.get_rect()
        
        # Now modify the collision box size
        self.rect.width = self.rect.width // 8
        self.rect.height = self.rect.height // 4
        
        # Animation variables
        self.current_frame = 0
        self.animation_speed = 0.15
        self.animation_timer = 0
        self.facing_left = False
        self.is_attacking = False
        
        # Separate ranges for animation and damage (reduced by 1/3)
        self.attack_animation_distance = 50  # Reduced from 50 to ~33
        self.attack_damage_distance = 50     # Reduced from 100 to ~66
        
        self.attack_frame = 0
        
        # Adjust sprite offset for better positioning
        self.sprite_offset_x = -25
        self.sprite_offset_y = -60
        
        self.player = player
        
        # Set speed based on level
        if level == 1:
            self.speed = LEVEL_1_SPEED
        elif level == 2:
            self.speed = LEVEL_2_SPEED
        else:
            self.speed = LEVEL_3_SPEED
        
        # Spawn enemy outside the screen
        side = random.randint(0, 3)
        if side == 0:  # Top
            self.rect.x = random.randint(0, WINDOW_WIDTH)
            self.rect.y = -50
        elif side == 1:  # Right
            self.rect.x = WINDOW_WIDTH + 50
            self.rect.y = random.randint(0, WINDOW_HEIGHT)
        elif side == 2:  # Bottom
            self.rect.x = random.randint(0, WINDOW_WIDTH)
            self.rect.y = WINDOW_HEIGHT + 50
        else:  # Left
            self.rect.x = -50
            self.rect.y = random.randint(0, WINDOW_HEIGHT)

    def update(self):
        # Calculate distance to player
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        dist = math.sqrt(dx ** 2 + dy ** 2)
        
        # Update facing direction
        new_facing_left = dx < 0
        
        # Check if close enough to attack
        self.is_attacking = dist <= self.attack_animation_distance
        
        if dist != 0:
            # Move towards player if not in attack animation range
            if not self.is_attacking:
                self.rect.x += self.speed * dx / dist
                self.rect.y += self.speed * dy / dist
            
            # Update animation
            self.animation_timer += self.animation_speed
            if self.animation_timer >= 1:
                self.animation_timer = 0
                if self.is_attacking:
                    # Use attack animation
                    self.current_frame = (self.current_frame + 1) % len(self.attack_frames_right)
                    if new_facing_left:
                        self.image = self.attack_frames_left[self.current_frame]
                    else:
                        self.image = self.attack_frames_right[self.current_frame]
                else:
                    # Reset attack frame when not attacking
                    self.attack_frame = 0
                    # Use walk animation
                    self.current_frame = (self.current_frame + 1) % len(self.walk_frames_right)
                    if new_facing_left:
                        self.image = self.walk_frames_left[self.current_frame]
                    else:
                        self.image = self.walk_frames_right[self.current_frame]
            
            self.facing_left = new_facing_left

    def draw(self, surface):
        # Draw the sprite at an offset from the collision box
        sprite_pos = (self.rect.x + self.sprite_offset_x, 
                     self.rect.y + self.sprite_offset_y)
        surface.blit(self.image, sprite_pos)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Vampire Survivors Clone")
        self.clock = pygame.time.Clock()
        self.running = True
        self.in_main_menu = True
        
        # Load menu images first
        self.foreground = pygame.image.load(os.path.join('assets', 'foreground.png'))
        self.foreground = pygame.transform.scale(self.foreground, (WINDOW_WIDTH, WINDOW_HEIGHT))
        
        # Load all background images
        self.backgrounds = {
            1: pygame.image.load(os.path.join('assets', 'background1.png')),
            2: pygame.image.load(os.path.join('assets', 'background2.png')),
            3: pygame.image.load(os.path.join('assets', 'background3.png'))
        }
        
        # Scale all backgrounds
        for level in self.backgrounds:
            self.backgrounds[level] = pygame.transform.scale(
                self.backgrounds[level], 
                (WINDOW_WIDTH, WINDOW_HEIGHT)
            )
        
        # Font for menu
        self.font = pygame.font.Font(None, 36)
        
        # Main menu buttons
        button_width = 200
        button_height = 50
        button_spacing = 20
        start_y = WINDOW_HEIGHT // 2
        
        # Menu buttons
        self.start_button = pygame.Rect(
            (WINDOW_WIDTH - button_width) // 2,
            start_y,
            button_width,
            button_height
        )
        
        self.settings_button = pygame.Rect(
            (WINDOW_WIDTH - button_width) // 2,
            start_y + button_height + button_spacing,
            button_width,
            button_height
        )
        
        self.menu_quit_button = pygame.Rect(
            (WINDOW_WIDTH - button_width) // 2,
            start_y + (button_height + button_spacing) * 2,
            button_width,
            button_height
        )
        
        # Game over and completion screen buttons
        self.restart_button = pygame.Rect(
            WINDOW_WIDTH//2 - button_width - button_spacing,
            WINDOW_HEIGHT//2 + 80,
            button_width,
            button_height
        )
        
        self.quit_button = pygame.Rect(
            WINDOW_WIDTH//2 + button_spacing,
            WINDOW_HEIGHT//2 + 80,
            button_width,
            button_height
        )
        
        # Initialize game variables but don't create sprites yet
        self.initialize_game_variables()

    def initialize_game_variables(self):
        """Initialize all game variables but don't create sprites until game starts"""
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.sing_attacks = pygame.sprite.Group()
        self.player = None  # Don't create player yet
        self.level = 1
        self.score = 0
        self.enemies_killed = 0
        self.transitioning = False
        self.game_over = False
        
        # Add shooting variables
        self.shot_delay = 250  # milliseconds between shots
        self.last_shot = 0
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = 1000
        self.transition_delay = 3000  # 3 seconds for level transition
        self.transition_timer = 0

    def reset_game(self):
        """Create player and reset game state when starting new game"""
        self.in_main_menu = False
        self.level = 1
        self.score = 0
        self.enemies_killed = 0
        self.transitioning = False
        self.game_over = False
        self.enemies_for_level = self.get_required_enemies()
        
        # Clear all sprites
        self.all_sprites.empty()
        self.enemies.empty()
        self.projectiles.empty()
        self.sing_attacks.empty()
        
        # Create player only when starting game
        self.player = Player()
        self.all_sprites.add(self.player)
        
        # Reset timers
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = 1000
        self.last_shot = 0

    def get_required_enemies(self):
        if self.level == 1:
            return LEVEL_1_ENEMIES
        elif self.level == 2:
            return LEVEL_2_ENEMIES
        else:
            return LEVEL_3_ENEMIES

    def show_level_transition(self):
        # Create semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))
        
        # Show level completion message
        if self.level < 3:
            level_text = self.font.render(f'Level {self.level} Complete!', True, WHITE)
            next_text = self.font.render(f'Preparing Level {self.level + 1}...', True, WHITE)
            
            # Center the text
            level_rect = level_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20))
            next_rect = next_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))
            
            # Draw the text
            self.screen.blit(level_text, level_rect)
            self.screen.blit(next_text, next_rect)
        else:
            # Special completion message for level 3
            congrats_text = self.font.render('Congratulations!', True, WHITE)
            clear_text = self.font.render('You have cleared this infected zone.', True, WHITE)
            
            # Center the text with more spacing
            congrats_rect = congrats_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30))
            clear_rect = clear_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30))
            
            # Draw the text
            self.screen.blit(congrats_text, congrats_rect)
            self.screen.blit(clear_text, clear_rect)
            
            # Draw buttons for completion screen
            pygame.draw.rect(self.screen, WHITE, self.restart_button, 2)
            pygame.draw.rect(self.screen, WHITE, self.quit_button, 2)

            # Draw button text
            restart_text = self.font.render('Restart', True, WHITE)
            quit_text = self.font.render('Quit', True, WHITE)
            
            restart_text_rect = restart_text.get_rect(center=self.restart_button.center)
            quit_text_rect = quit_text.get_rect(center=self.quit_button.center)
            
            self.screen.blit(restart_text, restart_text_rect)
            self.screen.blit(quit_text, quit_text_rect)

    def show_game_over(self):
        # Create semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(192)
        self.screen.blit(overlay, (0, 0))
        
        # Show game over message
        game_over_text = self.font.render('Game Over!', True, RED)
        score_text = self.font.render(f'Enemies Killed: {self.enemies_killed}', True, WHITE)
        level_text = self.font.render(f'Level Reached: {self.level}', True, WHITE)
        
        # Center the text
        game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40))
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        level_rect = level_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40))
        
        # Draw the text
        self.screen.blit(game_over_text, game_over_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(level_text, level_rect)

        # Draw buttons
        pygame.draw.rect(self.screen, WHITE, self.restart_button, 2)
        pygame.draw.rect(self.screen, WHITE, self.quit_button, 2)

        # Draw button text
        restart_text = self.font.render('Restart', True, WHITE)
        quit_text = self.font.render('Quit', True, WHITE)
        
        restart_text_rect = restart_text.get_rect(center=self.restart_button.center)
        quit_text_rect = quit_text.get_rect(center=self.quit_button.center)
        
        self.screen.blit(restart_text, restart_text_rect)
        self.screen.blit(quit_text, quit_text_rect)

    def show_main_menu(self):
        # Draw foreground
        self.screen.blit(self.foreground, (0, 0))
        
        # Draw buttons
        for button, text in [
            (self.start_button, 'Start'),
            (self.settings_button, 'Settings'),
            (self.menu_quit_button, 'Quit')
        ]:
            pygame.draw.rect(self.screen, WHITE, button, 2)
            button_text = self.font.render(text, True, WHITE)
            text_rect = button_text.get_rect(center=button.center)
            self.screen.blit(button_text, text_rect)

    def handle_menu_click(self, pos):
        if self.start_button.collidepoint(pos):
            self.in_main_menu = False
            self.reset_game()
        elif self.settings_button.collidepoint(pos):
            # Add settings functionality later
            pass
        elif self.menu_quit_button.collidepoint(pos):
            self.running = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if self.in_main_menu:
                    self.handle_menu_click(mouse_pos)
                elif (self.game_over or (self.level == 3 and self.enemies_killed >= LEVEL_3_ENEMIES)):
                    if self.restart_button.collidepoint(mouse_pos):
                        self.reset_game()
                    elif self.quit_button.collidepoint(mouse_pos):
                        self.running = False
            
            # Only handle other events if not in main menu
            if not self.in_main_menu:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_e:
                        self.player.sing_attack(self)
                    elif event.key == pygame.K_t:
                        if self.level < 3:
                            self.enemies_killed = self.enemies_for_level
                            self.check_level_up()
                    elif event.key == pygame.K_SPACE:
                        if not self.player.is_recharging:
                            if self.player.shoot():
                                self.player.is_shooting = True
                                self.player.shot_frame = 0
                                self.shoot()

        # Only handle continuous space press if not in main menu
        if not self.in_main_menu:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] and not self.player.is_recharging:
                current_time = pygame.time.get_ticks()
                if current_time - self.last_shot > self.shot_delay:
                    if self.player.shoot():
                        self.shoot()
                        self.last_shot = current_time

    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.shot_delay:
            if self.level == 1:
                # Single straight projectile for level 1
                self.shoot_single()
            elif self.level == 2:
                # Three bullets at once for level 2
                self.shoot_triple()
            else:
                # Arc attack for level 3
                self.shoot_arc()
            self.last_shot = current_time

    def shoot_triple(self):
        # Center bullet
        self.shoot_single()
        
        # Left bullet (offset by 15 degrees)
        angle_left = math.atan2(-self.player.last_direction[1], self.player.last_direction[0]) - math.radians(15)
        direction_left = (math.cos(angle_left), -math.sin(angle_left))
        projectile_left = Projectile(
            self.player.rect.centerx,
            self.player.rect.centery,
            direction_left
        )
        self.all_sprites.add(projectile_left)
        self.projectiles.add(projectile_left)
        
        # Right bullet (offset by 15 degrees)
        angle_right = math.atan2(-self.player.last_direction[1], self.player.last_direction[0]) + math.radians(15)
        direction_right = (math.cos(angle_right), -math.sin(angle_right))
        projectile_right = Projectile(
            self.player.rect.centerx,
            self.player.rect.centery,
            direction_right
        )
        self.all_sprites.add(projectile_right)
        self.projectiles.add(projectile_right)

    def shoot_single(self):
        projectile = Projectile(
            self.player.rect.centerx,
            self.player.rect.centery,
            self.player.last_direction
        )
        self.all_sprites.add(projectile)
        self.projectiles.add(projectile)

    def shoot_arc(self):
        # Calculate the base angle from player's direction
        base_angle = math.degrees(math.atan2(-self.player.last_direction[1], 
                                            self.player.last_direction[0]))
        
        # Calculate spread between projectiles
        angle_step = ARC_SPREAD / (ARC_PROJECTILE_COUNT - 1)
        start_angle = base_angle - (ARC_SPREAD / 2)
        
        # Create arc of projectiles
        for i in range(ARC_PROJECTILE_COUNT):
            angle = math.radians(start_angle + (angle_step * i))
            direction = (math.cos(angle), -math.sin(angle))
            
            projectile = Projectile(
                self.player.rect.centerx,
                self.player.rect.centery,
                direction
            )
            self.all_sprites.add(projectile)
            self.projectiles.add(projectile)

    def spawn_enemy(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.enemy_spawn_timer > self.enemy_spawn_delay:
            # Spawn multiple enemies based on level
            spawn_amount = 1 if self.level == 1 else 3 if self.level == 2 else 2
            
            for _ in range(spawn_amount):
                enemy = Enemy(self.player, self.level)
                self.all_sprites.add(enemy)
                self.enemies.add(enemy)
            
            self.enemy_spawn_timer = current_time

    def check_collisions(self):
        # Check player collision with enemies that are in damage range
        for enemy in self.enemies:
            dx = self.player.rect.centerx - enemy.rect.centerx
            dy = self.player.rect.centery - enemy.rect.centery
            dist = math.sqrt(dx ** 2 + dy ** 2)
            
            if dist <= enemy.attack_damage_distance:
                if not self.player.invulnerable:
                    self.player.health -= 5
                    self.player.take_damage()
                    if self.player.health <= 0:
                        self.player.die()  # Start death animation
                        self.transition_timer = pygame.time.get_ticks()

        # Count enemies killed by projectiles
        projectile_hits = pygame.sprite.groupcollide(self.projectiles, self.enemies, True, True)
        self.enemies_killed += len(projectile_hits)
        
        # Count enemies killed by sing attack
        for sing in self.sing_attacks:
            sing_hits = pygame.sprite.spritecollide(sing, self.enemies, True)
            self.enemies_killed += len(sing_hits)
        
        self.check_level_up()

    def check_level_up(self):
        if self.enemies_killed >= self.enemies_for_level and not self.transitioning:
            self.transitioning = True
            self.transition_timer = pygame.time.get_ticks()
            # Clear all enemies from screen
            for enemy in self.enemies:
                enemy.kill()
            
            # Don't end the game immediately when level 3 is complete
            if self.level == 3:
                self.game_over = True  # Show game over screen instead

    def handle_level_transition(self):
        if self.transitioning:
            current_time = pygame.time.get_ticks()
            if current_time - self.transition_timer >= self.transition_delay:
                self.level += 1
                self.enemies_killed = 0
                self.enemies_for_level = self.get_required_enemies()
                # Adjust spawn delay based on level
                if self.level == 2:
                    self.enemy_spawn_delay = 1500  # Longer delay for multiple spawns
                else:
                    self.enemy_spawn_delay = 1000
                self.transitioning = False

    def draw_hud(self):
        # Draw health bar
        health_width = 200 * (self.player.health / self.player.max_health)
        pygame.draw.rect(self.screen, RED, (10, 10, health_width, 20))
        pygame.draw.rect(self.screen, WHITE, (10, 10, 200, 20), 2)
        
        # Draw level info
        level_text = self.font.render(f'Level: {self.level}', True, WHITE)
        self.screen.blit(level_text, (10, 40))
        
        # Draw enemies killed progress
        progress_text = self.font.render(
            f'Enemies: {self.enemies_killed}/{self.enemies_for_level}', 
            True, WHITE
        )
        self.screen.blit(progress_text, (10, 70))
        
        # Draw ammo counter
        ammo_text = self.font.render(f'Ammo: {self.player.current_ammo}/{self.player.max_ammo}', True, WHITE)
        self.screen.blit(ammo_text, (10, 100))  # Position below enemies counter
        
        # Show "RECHARGING" text when recharging
        if self.player.is_recharging:
            recharge_text = self.font.render('RECHARGING...', True, YELLOW)
            self.screen.blit(recharge_text, (10, 130))

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            
            if self.in_main_menu:
                self.show_main_menu()
                pygame.display.flip()
            else:
                current_time = pygame.time.get_ticks()
                
                # Check if death animation is complete
                if self.player.is_dead and not self.game_over:
                    if current_time - self.player.death_start_time >= self.player.death_duration:
                        self.game_over = True
                
                # Only update game if not in transition, not dead, and not game over
                if not self.transitioning and not self.game_over and not self.player.is_dead:
                    if not (self.level == 3 and self.enemies_killed >= LEVEL_3_ENEMIES):
                        self.spawn_enemy()
                    self.all_sprites.update()
                    self.check_collisions()
                elif self.player.is_dead:
                    self.player.update()
                
                self.handle_level_transition()
                
                # Draw game
                self.screen.blit(self.backgrounds[self.level], (0, 0))
                
                for sprite in self.all_sprites:
                    if sprite != self.player and not isinstance(sprite, Enemy):
                        self.screen.blit(sprite.image, sprite.rect)
                
                for enemy in self.enemies:
                    enemy.draw(self.screen)
                
                self.player.draw(self.screen)
                
                self.draw_hud()
                
                # Show appropriate overlay screen
                if self.transitioning:
                    self.show_level_transition()
                elif self.game_over:
                    self.show_game_over()
                
                pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run() 