# entities.py
import random
import pygame
import math
import random
from abc import ABC, abstractmethod
from settings import *
from api_logger import APILogger

# --- ASSETS & AUDIO MANAGER ---
import os
import sys

def load_image_fallback(path, fallback_func, size):
    """Try to load an image, fallback to procedural drawing if it fails."""
    # Robust path construction: relative to this file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Handle PyInstaller _MEIPASS for bundled resources
    if hasattr(sys, '_MEIPASS'):
        base_dir = sys._MEIPASS

    # Construct the absolute path
    # NOTE: We use *path.replace to handle mixed slashes from different OS inputs
    norm_path = os.path.join(base_dir, *path.replace('\\', '/').split('/'))
    
    try:
        # 1. Try the exact path first
        if os.path.exists(norm_path):
            img = pygame.image.load(norm_path).convert_alpha()
            print(f"LOADER: [SUCCESS] Loaded Image from {norm_path}")
            return pygame.transform.scale(img, size)
        
        # Try a sibling match (same name, different extension)
        base_no_ext, ext = os.path.splitext(norm_path)
        for alt_ext in ['.png', '.jpg', '.jpeg', '.bmp']:
            if alt_ext.lower() != ext.lower():
                alt_path = base_no_ext + alt_ext
                if os.path.exists(alt_path):
                    img = pygame.image.load(alt_path).convert_alpha()
                    print(f"LOADER: [SUCCESS] Found Image with alt extension: {alt_path}")
                    return pygame.transform.scale(img, size)
                
        # Try looking in the root directory (one level up from assets folder)
        root_match = os.path.join(base_dir, os.path.basename(path))
        if os.path.exists(root_match):
            img = pygame.image.load(root_match).convert_alpha()
            print(f"LOADER: [SUCCESS] Found Image in root directory: {root_match}")
            return pygame.transform.scale(img, size)
            
    except Exception as e:
        print(f"LOADER: [ERROR] Failed to load asset {path}: {e}")

    # Final Fallback: Procedural
    print(f"LOADER: [FALLBACK] Using procedural drawing for {path}")
    surf = pygame.Surface(size, pygame.SRCALPHA).convert_alpha()
    fallback_func(surf, size[0]//2, size[1]//2)
    return surf

def draw_circular_timer(screen, center, progress, color, radius=15):
    """Draws a circular 'clock' timer representing power-up progress."""
    rect = pygame.Rect(center[0] - radius, center[1] - radius, radius * 2, radius * 2)
    # Background circle (dim)
    pygame.draw.circle(screen, (50, 50, 50, 150), center, radius)
    # Arc representing remaining time
    # progress is 0.0 (full) to 1.0 (empty) or vice versa? 
    # Let's say progress is 1.0 -> 0.0 (time left)
    angle = progress * 2 * math.pi
    if angle > 0:
        # pygame.draw.arc uses radians. Start at top (-pi/2)
        pygame.draw.arc(screen, color, rect, -math.pi/2, -math.pi/2 + angle, 3)

class AudioManager:
    _instance = None
    _sounds = {}
    _music_on = True
    _sound_on = True

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AudioManager, cls).__new__(cls)
            cls._instance._init_mixer()
        return cls._instance

    def _init_mixer(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except:
            print("Audio Mixer failed to initialize.")

    def _get_abs_path(self, file):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if hasattr(sys, '_MEIPASS'):
            base_dir = sys._MEIPASS
        return os.path.join(base_dir, file)

    def load_sounds(self):
        """Lazy loading of sounds with absolute paths"""
        sound_files = {
            'shoot': 'shoot.wav',
            'explosion': 'explosion.wav'
        }
        for name, file in sound_files.items():
            abs_p = self._get_abs_path(file)
            try:
                if os.path.exists(abs_p):
                    self._sounds[name] = pygame.mixer.Sound(abs_p)
                    if name == 'shoot': self._sounds[name].set_volume(0.4)
                    if name == 'explosion': self._sounds[name].set_volume(0.5)
                else:
                    print(f"DEBUG: Sound file not found: {abs_p}")
                    self._sounds[name] = None
            except Exception as e:
                self._sounds[name] = None
                print(f"Warning: Could not load sound {file}: {e}")

    def play_sound(self, name):
        if self._sound_on and name in self._sounds and self._sounds[name]:
            self._sounds[name].play()

    def toggle_sound(self):
        self._sound_on = not self._sound_on
        return self._sound_on

    def play_music(self, file, loop=-1):
        if not self._music_on: return
        abs_p = self._get_abs_path(file)
        try:
            if os.path.exists(abs_p):
                pygame.mixer.music.load(abs_p)
                pygame.mixer.music.play(loop)
            else:
                print(f"DEBUG: Music file not found: {abs_p}")
        except Exception as e:
            print(f"Warning: Could not play music {file}: {e}")

    def stop_music(self):
        pygame.mixer.music.stop()

# Initialize global instance
AUDIO = AudioManager()

# --- OPTIMIZATION: SURFACE CACHE ---
# Pre-render some common surfaces to avoid lag in draw() calls.
PARTICLE_SURFACES = []
# Dummy Fallback Surfaces to prevent NoneType errors in builds
DUMMY_SURF = pygame.Surface((1,1), pygame.SRCALPHA)
HEART_SURFACE = DUMMY_SURF
SHIELD_EMBLEM_SURFACE = DUMMY_SURF
DRONE_SURFACE = DUMMY_SURF
HUNTER_SURFACE = DUMMY_SURF
HEAVY_SURFACE = DUMMY_SURF
JET_SURFACE = DUMMY_SURF
JET_FLAME_SURFACE = DUMMY_SURF
RAPID_SURFACE = DUMMY_SURF
SHIELD_AURA_SURF = DUMMY_SURF
GLOW_SURFACES_LIFE = [DUMMY_SURF] * 10
GLOW_SURFACES_SHIELD = [DUMMY_SURF] * 10
GLOW_SURFACES_RAPID = [DUMMY_SURF] * 10

def cache_particles():
    global PARTICLE_SURFACES
    PARTICLE_SURFACES = []
    for i in range(1, 21): 
        r = 10 + (20 - i)
        s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        alpha = int((i / 20) * 255)
        color = (255, int(i * 10), 0)
        pygame.draw.circle(s, (*color, alpha), (r, r), r)
        PARTICLE_SURFACES.append(s)

def cache_glows():
    global GLOW_SURFACES_LIFE, GLOW_SURFACES_SHIELD, GLOW_SURFACES_RAPID
    GLOW_SURFACES_LIFE = []
    GLOW_SURFACES_SHIELD = []
    GLOW_SURFACES_RAPID = []
    for i in range(10):
        size = int(30 + i * 2) 
        s_life = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.circle(s_life, (0, 255, 0, 50), (size, size), size)
        GLOW_SURFACES_LIFE.append(s_life)
        s_shield = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.circle(s_shield, (0, 100, 255, 50), (size, size), size)
        GLOW_SURFACES_SHIELD.append(s_shield)
        
        s_rapid = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.circle(s_rapid, (255, 255, 0, 50), (size, size), size)
        GLOW_SURFACES_RAPID.append(s_rapid)

def cache_static_assets():
    global HEART_SURFACE, SHIELD_EMBLEM_SURFACE, DRONE_SURFACE, HUNTER_SURFACE, HEAVY_SURFACE, JET_SURFACE, JET_FLAME_SURFACE, RAPID_SURFACE
    # Heart
    HEART_SURFACE = pygame.Surface((40, 40), pygame.SRCALPHA)
    draw_heart_procedural(HEART_SURFACE, 20, 15, 25)
    
    # Shield
    SHIELD_EMBLEM_SURFACE = pygame.Surface((40, 40), pygame.SRCALPHA)
    draw_shield_emblem_procedural(SHIELD_EMBLEM_SURFACE, 20, 20, 25)
    
    # Enemies (Images + Fallback)
    DRONE_SURFACE = load_image_fallback('img/enemy1.png', lambda s, x, y: draw_drone_procedural(s, x, y), (60, 60))
    # Try specific images for Hunter and Heavy if they exist, otherwise fallback to enemy1 or procedural
    HUNTER_SURFACE = load_image_fallback('img/enemy1.png', 
                                         lambda s, x, y: load_image_fallback('img/enemy1.png', 
                                                                            lambda s2, x2, y2: pygame.draw.circle(s2, (255, 50, 50), (x2, y2), 18), (40, 40)), (40, 40))
    HEAVY_SURFACE = load_image_fallback('img/enemy1.png', 
                                         lambda s, x, y: load_image_fallback('img/enemy1.png', 
                                                                            lambda s2, x2, y2: pygame.draw.circle(s2, (150, 0, 200), (x2, y2), 28), (60, 60)), (60, 60))
    
    # Jet (Player Ship) - Now with image loading and rounded fallback
    JET_SURFACE = load_image_fallback('img/player_ship.jpg', lambda s, x, y: draw_jet_procedural(s, x, y), (60, 80))
    
    # Jet Flame
    JET_FLAME_SURFACE = pygame.Surface((20, 40), pygame.SRCALPHA)
    pygame.draw.polygon(JET_FLAME_SURFACE, (255, 150, 0), [(0, 0), (20, 0), (10, 30)])
    pygame.draw.polygon(JET_FLAME_SURFACE, (255, 255, 0), [(5, 0), (15, 0), (10, 15)])
    
    # Rapid Fire Icon
    RAPID_SURFACE = pygame.Surface((30, 30), pygame.SRCALPHA)
    for i in range(-1, 2):
        pygame.draw.rect(RAPID_SURFACE, (255, 255, 0), (15 + i*8 - 2, 10, 4, 10))
    
    # Shield Aura Surface
    global SHIELD_AURA_SURF
    SHIELD_AURA_SURF = pygame.Surface((120, 120), pygame.SRCALPHA)
    pygame.draw.circle(SHIELD_AURA_SURF, (0, 255, 255, 80), (60, 60), 50)
    pygame.draw.circle(SHIELD_AURA_SURF, (0, 255, 255, 255), (60, 60), 50, 2)

def draw_heart_procedural(surf, x, y, size):
    r = size // 2
    color = (255, 50, 50)
    pygame.draw.circle(surf, color, (x - r//2, y), r//2)
    pygame.draw.circle(surf, color, (x + r//2, y), r//2)
    points = [(x - r, y + r//4), (x + r, y + r//4), (x, y + r)]
    pygame.draw.polygon(surf, color, points)

def draw_shield_emblem_procedural(surf, x, y, size):
    w, h = size, size
    color = (50, 150, 255)
    points = [
        (x - w//2, y - size//2), (x + w//2, y - size//2),
        (x + w//2, y), (x, y + size//2), (x - w//2, y)
    ]
    pygame.draw.polygon(surf, color, points)
    pygame.draw.polygon(surf, (255, 255, 255), points, 2)

def draw_drone_procedural(surf, cx, cy):
    # Outer wing frames
    pygame.draw.line(surf, (100, 100, 100), (cx-25, cy-25), (cx+25, cy+25), 2)
    pygame.draw.line(surf, (100, 100, 100), (cx+25, cy-25), (cx-25, cy+25), 2)
    # Diamond body
    points = [(cx, cy-22), (cx+22, cy), (cx, cy+22), (cx-22, cy)]
    pygame.draw.polygon(surf, (30, 30, 30), points)
    pygame.draw.polygon(surf, (80, 80, 80), points, 2)

def draw_jet_procedural(surf, cx, cy):
    # Sleek, rounded ship design
    # Wings (Rounded Elipses)
    pygame.draw.ellipse(surf, (80, 80, 100), (cx - 28, cy - 5, 56, 25))
    pygame.draw.ellipse(surf, (100, 100, 120), (cx - 25, cy - 5, 50, 20))
    
    # Fuselage (Rounded)
    pygame.draw.ellipse(surf, COLOR_PLAYER, (cx - 12, cy - 25, 24, 65))
    
    # Cockpit (Glass)
    pygame.draw.ellipse(surf, (0, 200, 255), (cx - 6, cy - 15, 12, 22))
    
    # Highlights
    pygame.draw.ellipse(surf, (255, 255, 255, 100), (cx - 4, cy - 12, 4, 10))

# Global function to draw heart using cache
def draw_heart(screen, x, y, size=None):
    screen.blit(HEART_SURFACE, (x - 20, y - 15))

def draw_shield_emblem(screen, x, y, size=None):
    screen.blit(SHIELD_EMBLEM_SURFACE, (x - 20, y - 20))

def initialize_entities():
    """
    Consolidated initialization for all procedurally generated assets.
    Call this AFTER pygame.init() and set_mode().
    """
    cache_particles()
    cache_glows()
    cache_static_assets()
    AUDIO.load_sounds()

# --- ABSTRACT BASE ---
class GameEntity(ABC):
    @abstractmethod
    def update(self): pass
    @abstractmethod
    def draw(self, screen): pass

# --- VISUALS: PARTICLE SYSTEM (Explosions) ---
class Particle(GameEntity):
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.life = 20
        self.radius = 10

    def update(self):
        self.life -= 1
        self.radius += 1

    def draw(self, screen):
        if self.life > 0:
            # Use pre-rendered surface based on life stage
            idx = max(0, min(self.life - 1, 19))
            surf = PARTICLE_SURFACES[idx]
            screen.blit(surf, (self.x - surf.get_width()//2, self.y - surf.get_height()//2))

# --- PATTERN: COMPOSITE ---
# The Drone, Hunter, and Heavy are 'Leaf' nodes.
# EnemySquadron is the 'Composite' node that contains them.
# This allows the Game Loop to treat a single enemy and a group of enemies identically.
# Both inherit from GameEntity to ensure interface consistency.
class Drone(GameEntity):
    def __init__(self, x, y, speed_mod=0):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.hp = 1
        self.speed = ENEMY_BASE_SPEED + speed_mod
        self.wobble = float(x) # For sine wave movement

    def update(self):
        self.rect.y += self.speed
        self.wobble += 0.1
        self.rect.x += math.sin(self.wobble) * 2 # Real movement logic

    def draw(self, screen):
        # Draw body from cache
        screen.blit(DRONE_SURFACE, (self.rect.x - 10, self.rect.y - 10))
        
        # Pulsing Red Eye
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 100
        eye_color = (155 + pulse, 0, 0)
        cx, cy = self.rect.centerx, self.rect.centery
        pygame.draw.circle(screen, eye_color, (cx, cy), 10)
        pygame.draw.circle(screen, (255, 255, 255), (cx-3, cy-3), 3) # Highlight
        
        # Laser sight (flickering)
        if pygame.time.get_ticks() % 100 > 30:
            pygame.draw.line(screen, (255, 0, 0, 100), (cx, cy), (cx, cy+40), 1)

class Hunter(GameEntity):
    def __init__(self, x, y, speed_mod=0):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.hp = 1
        self.speed = HUNTER_SPEED + speed_mod
        self.wobble = float(x)

    def update(self):
        self.rect.y += self.speed
        self.wobble += 0.15
        self.rect.x += math.sin(self.wobble) * 4 # Faster wobble

    def draw(self, screen):
        screen.blit(HUNTER_SURFACE, (self.rect.x, self.rect.y))
        # Marker: Red Triangle floating above
        tx, ty = self.rect.centerx, self.rect.top - 10
        pygame.draw.polygon(screen, (255, 0, 0), [(tx, ty), (tx-5, ty-10), (tx+5, ty-10)])

class Heavy(GameEntity):
    def __init__(self, x, y, speed_mod=0):
        self.rect = pygame.Rect(x, y, 60, 60)
        self.hp = 2 # 2 HP for Heavy
        self.speed = HEAVY_SPEED + speed_mod

    def update(self):
        self.rect.y += self.speed

    def draw(self, screen):
        screen.blit(HEAVY_SURFACE, (self.rect.x, self.rect.y))
        # HP Bar (small)
        pygame.draw.rect(screen, (255, 0, 0), (self.rect.x, self.rect.y - 5, 60, 4))
        pygame.draw.rect(screen, (0, 255, 0), (self.rect.x, self.rect.y - 5, 30 * self.hp, 4))

# --- NEW ENTITY: OBSTACLE (Asteroid) ---
class Asteroid(GameEntity):
    """
    Static/Drifting obstacle. 
    Does not target the player but drifts across the screen.
    """
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 50)
        self.speed_x = random.uniform(-1, 1)
        self.speed_y = random.uniform(1, 3)
        self.rotation = 0
        self.rot_speed = random.uniform(1, 5)
        # GENERATE POINTS ONCE
        self.points_relative = []
        for i in range(8):
            angle = math.radians(i * 45)
            r = 20 + random.randint(0, 5)
            self.points_relative.append((math.cos(angle) * r, math.sin(angle) * r))

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        self.rotation += self.rot_speed

    def draw(self, screen):
        cx, cy = self.rect.center
        # Rotate pre-generated points
        rad = math.radians(self.rotation)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        
        rotated_points = []
        for dx, dy in self.points_relative:
            rx = dx * cos_a - dy * sin_a
            ry = dx * sin_a + dy * cos_a
            rotated_points.append((cx + rx, cy + ry))
        
        pygame.draw.polygon(screen, (80, 70, 60), rotated_points) # Brown Rock
        pygame.draw.polygon(screen, (120, 110, 100), rotated_points, 2) # Highlight

class EnemySquadron(GameEntity):
    def __init__(self):
        self.children = []
        self.particles = []

    def add(self, entity):
        self.children.append(entity)
        # Reduce logging frequency
        # APILogger().log("ENTITY_CREATE", f"Spawned {entity.__class__.__name__}")

    def add_explosion(self, x, y):
        self.particles.append(Particle(x, y))
        AUDIO.play_sound('explosion')
        # APILogger().log("COLLISION", "Explosion triggered at location")

    def update(self):
        for child in self.children:
            child.update()
        for p in self.particles[:]:
            p.update()
            if p.life <= 0: self.particles.remove(p)

    def draw(self, screen):
        for child in self.children:
            child.draw(screen)
        for p in self.particles:
            p.draw(screen)

# --- PATTERN: DECORATOR ---
# The abstract 'Ship' class defines the component interface.
# 'FighterJet' is the Concrete Component (the base object).
# 'RapidFireDecorator' and 'ShieldDecorator' are Concrete Decorators that wrap the ship.
# KEY FEATURE: These decorators stack recursively (e.g., Shield(Rapid(Ship))).
class Ship(ABC):
    @abstractmethod
    def update(self): pass
    @abstractmethod
    def shoot(self, bullets_list): pass
    @abstractmethod
    def draw(self, screen): pass
    @abstractmethod
    def get_rect(self): pass
    @abstractmethod
    def move(self, dx): pass
    @abstractmethod
    def set_x(self, x): pass
    @abstractmethod
    def take_damage(self): pass # Returns True if dead, False if survived, or "BREAK_SHIELD"
    @abstractmethod
    def get_base_ship(self): pass
    @abstractmethod
    def has_decorator(self, cls): pass
    @abstractmethod
    def remove_decorator(self, cls): pass

class FighterJet(Ship):
    def __init__(self):
        self.rect = pygame.Rect(375, 500, 40, 50)
        self.lives = 3 # New: 3 Lives System

    def update(self): 
        return None # Fighters don't expire

    def set_x(self, x):
        self.rect.centerx = x
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - 40))

    def take_damage(self):
        self.lives -= 1
        APILogger().log("DAMAGE", f"Hull Integrity Critical. Lives: {self.lives}")
        return self.lives <= 0

    def get_base_ship(self): return self
    def has_decorator(self, cls): return False
    def remove_decorator(self, cls): return self

    def move(self, dx):
        self.rect.x += dx
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - 40))

    def shoot(self, bullets_list):
        # Center cannon
        b = pygame.Rect(self.rect.centerx - 2, self.rect.top, 4, 15)
        bullets_list.append(b)
        AUDIO.play_sound('shoot')
        # APILogger().log("ACTION", "Cannon Fired")

    def draw(self, screen):
        cx, cy = self.rect.centerx, self.rect.centery
        
        # Engine Glow pulsing
        glow = abs(math.sin(pygame.time.get_ticks() * 0.01)) * 10
        pygame.draw.circle(screen, (0, 150, 255), (cx, cy + 20), 20 + glow, 1) # Hull Aura
        
        # Main Body from Cache
        screen.blit(JET_SURFACE, (self.rect.x - 10, self.rect.y - 15))
        
        # Engine Flame from Cache (Dynamic Position)
        flame_h = 15 + (pygame.time.get_ticks() % 10)
        # Scale flame height? No, just blit it
        screen.blit(JET_FLAME_SURFACE, (cx - 10, self.rect.bottom))

    def get_rect(self): return self.rect

class RapidFireDecorator(Ship):
    def __init__(self, wrapped_ship):
        self.ship = wrapped_ship
        self.start_time = pygame.time.get_ticks()
        self.duration = POWERUP_DURATION
        APILogger().log("UPGRADE", "Tactical Nuke/Rapid Fire Equipped")

    def update(self):
        # Propagate update and check for inner expiration
        res = self.ship.update()
        if res == "EXPIRED":
             # Unwrap the expired inner decorator
             # APILogger().log("DECORATOR_UNWRAP", f"Unwrapping {type(self.ship).__name__}")
             self.ship = self.ship.remove_decorator(type(self.ship))
        
        if pygame.time.get_ticks() - self.start_time > self.duration:
             return "EXPIRED"
        return None

    def move(self, dx): self.ship.move(dx)
    def set_x(self, x): self.ship.set_x(x)
    def take_damage(self): return self.ship.take_damage()
    def get_rect(self): return self.ship.get_rect()
    def get_base_ship(self): return self.ship.get_base_ship()
    def has_decorator(self, cls): 
        return isinstance(self, cls) or self.ship.has_decorator(cls)
    def remove_decorator(self, cls):
        if isinstance(self, cls): return self.ship
        self.ship = self.ship.remove_decorator(cls)
        return self

    def shoot(self, bullets_list):
        self.ship.shoot(bullets_list) # Middle shot
        # Wingman shots
        b1 = pygame.Rect(self.ship.get_rect().left, self.ship.get_rect().top + 10, 4, 15)
        b2 = pygame.Rect(self.ship.get_rect().right, self.ship.get_rect().top + 10, 4, 15)
        bullets_list.append(b1)
        bullets_list.append(b2)

    def draw(self, screen):
        self.ship.draw(screen)
        # Draw Energy Shield Aura
        pygame.draw.circle(screen, (0, 255, 255), self.ship.get_rect().center, 40, 1)

class ShieldDecorator(Ship):
    def __init__(self, wrapped_ship):
        self.ship = wrapped_ship
        self.start_time = pygame.time.get_ticks()
        self.duration = POWERUP_DURATION
        APILogger().log("UPGRADE", "Energy Shield Activated")

    def update(self):
        # Propagate update and check for inner expiration
        res = self.ship.update()
        if res == "EXPIRED":
             self.ship = self.ship.remove_decorator(type(self.ship))

        if pygame.time.get_ticks() - self.start_time > self.duration:
             return "EXPIRED"
        return None

    def move(self, dx): self.ship.move(dx)
    def set_x(self, x): self.ship.set_x(x)
    def get_rect(self): return self.ship.get_rect()

    def shoot(self, bullets_list):
        self.ship.shoot(bullets_list)

    def take_damage(self):
        # Shield absorbs damage then breaks!
        APILogger().log("DECORATOR_REMOVE", "ShieldDecorator removed from Ship")
        return "BREAK_SHIELD" # Special signal to Controller to unwrap
    
    def get_base_ship(self): return self.ship.get_base_ship()
    def has_decorator(self, cls): 
        return isinstance(self, cls) or self.ship.has_decorator(cls)
    def remove_decorator(self, cls):
        if isinstance(self, cls): return self.ship
        self.ship = self.ship.remove_decorator(cls)
        return self

    def draw(self, screen):
        self.ship.draw(screen)
        # Use cached shield aura for efficiency
        # Pulsing effect
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.01)) * 20
        # Scale? No, just draws at center
        screen.blit(SHIELD_AURA_SURF, (self.ship.get_rect().centerx - 60, self.ship.get_rect().centery - 60))
        # Extra glow
        if pulse > 10:
            pygame.draw.circle(screen, (0, 255, 255, 100), self.ship.get_rect().center, 52, 1)

# --- PATTERN: FACTORY / STRATEGY ---
# While simple, this acts as a factory creating different power-up types.
# The 'type_name' determines the strategy used when the player picks it up.
class PowerUp(GameEntity):
    def __init__(self, x, y, type_name):
        self.rect = pygame.Rect(x, y, 30, 30)
        self.type = type_name # 'SHIELD' or 'LIFE'
    
    def update(self):
        self.rect.y += 3 # Fall down
        
    def draw(self, screen):
        # Glow Effect using pre-rendered surfaces
        pulse_idx = int((math.sin(pygame.time.get_ticks() * 0.01) + 1) * 4.5) # 0 to 9 index
        pulse_idx = max(0, min(pulse_idx, 9))
        
        if self.type == 'LIFE':
            surf = GLOW_SURFACES_LIFE[pulse_idx] if pulse_idx < len(GLOW_SURFACES_LIFE) else DUMMY_SURF
            screen.blit(surf, (self.rect.centerx - surf.get_width()//2, self.rect.centery - surf.get_height()//2))
            if HEART_SURFACE: draw_heart(screen, self.rect.centerx, self.rect.centery - 5, 20)
        elif self.type == 'RAPID':
            surf = GLOW_SURFACES_RAPID[pulse_idx] if pulse_idx < len(GLOW_SURFACES_RAPID) else DUMMY_SURF
            screen.blit(surf, (self.rect.centerx - surf.get_width()//2, self.rect.centery - surf.get_height()//2))
            if RAPID_SURFACE: screen.blit(RAPID_SURFACE, (self.rect.x, self.rect.y))
        else: 
            # SHIELD
            surf = GLOW_SURFACES_SHIELD[pulse_idx] if pulse_idx < len(GLOW_SURFACES_SHIELD) else DUMMY_SURF
            screen.blit(surf, (self.rect.centerx - surf.get_width()//2, self.rect.centery - surf.get_height()//2))
            if SHIELD_EMBLEM_SURFACE: draw_shield_emblem(screen, self.rect.centerx, self.rect.centery, 25)
