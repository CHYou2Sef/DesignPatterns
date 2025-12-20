# entities.py
import pygame
import math
import random
from abc import ABC, abstractmethod
from settings import *
from api_logger import APILogger

# --- ASSETS & AUDIO MANAGER ---
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

    def load_sounds(self):
        """Lazy loading of sounds"""
        sound_files = {
            'shoot': 'shoot.wav',
            'explosion': 'explosion.wav'
        }
        for name, file in sound_files.items():
            try:
                self._sounds[name] = pygame.mixer.Sound(file)
                if name == 'shoot': self._sounds[name].set_volume(0.4)
                if name == 'explosion': self._sounds[name].set_volume(0.5)
            except:
                self._sounds[name] = None
                print(f"Warning: Could not load sound {file}")

    def play_sound(self, name):
        if self._sound_on and name in self._sounds and self._sounds[name]:
            self._sounds[name].play()

    def toggle_sound(self):
        self._sound_on = not self._sound_on
        return self._sound_on

    def play_music(self, file, loop=-1):
        if not self._music_on: return
        try:
            pygame.mixer.music.load(file)
            pygame.mixer.music.play(loop)
        except:
            print(f"Warning: Could not play music {file}")

    def stop_music(self):
        pygame.mixer.music.stop()

# Initialize global instance
AUDIO = AudioManager()

# --- OPTIMIZATION: SURFACE CACHE ---
# Pre-render some common surfaces to avoid lag in draw() calls.
PARTICLE_SURFACES = []
HEART_SURFACE = None
SHIELD_EMBLEM_SURFACE = None
DRONE_SURFACE = None
JET_SURFACE = None
JET_FLAME_SURFACE = None

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
    global GLOW_SURFACES_LIFE, GLOW_SURFACES_SHIELD
    for i in range(10):
        size = int(30 + i * 2) 
        s_life = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.circle(s_life, (0, 255, 0, 50), (size, size), size)
        GLOW_SURFACES_LIFE.append(s_life)
        s_shield = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.circle(s_shield, (0, 100, 255, 50), (size, size), size)
        GLOW_SURFACES_SHIELD.append(s_shield)

def cache_static_assets():
    global HEART_SURFACE, SHIELD_EMBLEM_SURFACE, DRONE_SURFACE, JET_SURFACE, JET_FLAME_SURFACE
    # Heart
    HEART_SURFACE = pygame.Surface((40, 40), pygame.SRCALPHA)
    draw_heart_procedural(HEART_SURFACE, 20, 15, 25)
    
    # Shield
    SHIELD_EMBLEM_SURFACE = pygame.Surface((40, 40), pygame.SRCALPHA)
    draw_shield_emblem_procedural(SHIELD_EMBLEM_SURFACE, 20, 20, 25)
    
    # Drone
    DRONE_SURFACE = pygame.Surface((60, 60), pygame.SRCALPHA)
    draw_drone_procedural(DRONE_SURFACE, 30, 30)
    
    # Jet
    JET_SURFACE = pygame.Surface((60, 80), pygame.SRCALPHA)
    draw_jet_procedural(JET_SURFACE, 30, 40)
    
    # Jet Flame
    JET_FLAME_SURFACE = pygame.Surface((20, 40), pygame.SRCALPHA)
    pygame.draw.polygon(JET_FLAME_SURFACE, (255, 150, 0), [(0, 0), (20, 0), (10, 30)])
    pygame.draw.polygon(JET_FLAME_SURFACE, (255, 255, 0), [(5, 0), (15, 0), (10, 15)])

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
    # Wings
    x, y = cx - 20, cy - 10
    pygame.draw.polygon(surf, (100, 100, 120), [(x, y+30), (x+40, y+30), (x+20, y)])
    pygame.draw.line(surf, (0, 255, 255), (x+5, y+30), (x+15, y+10), 2)
    pygame.draw.line(surf, (0, 255, 255), (x+35, y+30), (x+25, y+10), 2)
    # Fuselage
    pygame.draw.polygon(surf, COLOR_PLAYER, [(x+14, y+50), (x+26, y+50), (x+20, y-15)])
    # Cockpit
    pygame.draw.ellipse(surf, (0, 200, 255), (x+17, y+10, 6, 15))

# Global function to draw heart using cache
def draw_heart(screen, x, y, size=None):
    screen.blit(HEART_SURFACE, (x - 20, y - 15))

def draw_shield_emblem(screen, x, y, size=None):
    screen.blit(SHIELD_EMBLEM_SURFACE, (x - 20, y - 20))

# Call caching
cache_particles()
cache_glows()
cache_static_assets()

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
# The Drone is the 'Leaf', and EnemySquadron is the 'Composite'.
# Both inherit from GameEntity to allow uniform treatment.
class Drone(GameEntity):
    def __init__(self, x, y, speed_mod=0):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.speed = ENEMY_BASE_SPEED + speed_mod
        self.wobble = float(x) # For sine wave movement

    def update(self):
        self.rect.y += self.speed
        self.wobble += 0.1
        self.rect.x += math.sin(self.wobble) * 2 # Real movement logic

    def draw(self, screen):
        # Draw body from cache
        screen.blit(DRONE_SURFACE, (self.rect.x - 10, self.rect.y - 10))
        
        # Pulsing Red Eye (Static location on body, only color changes)
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 100
        eye_color = (155 + pulse, 0, 0)
        cx, cy = self.rect.centerx, self.rect.centery
        pygame.draw.circle(screen, eye_color, (cx, cy), 10)
        pygame.draw.circle(screen, (255, 255, 255), (cx-3, cy-3), 3) # Highlight
        
        # Laser sight (flickering) - optimized random
        if pygame.time.get_ticks() % 100 > 30:
            pygame.draw.line(screen, (255, 0, 0, 100), (cx, cy), (cx, cy+40), 1)

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
        APILogger().log("ENTITY_CREATE", f"Spawned {entity.__class__.__name__}")

    def add_explosion(self, x, y):
        self.particles.append(Particle(x, y))
        AUDIO.play_sound('explosion')
        APILogger().log("COLLISION", "Explosion triggered at location")

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
# The Ship is the 'Component'.
# RapidFireDecorator and ShieldDecorator are 'Concrete Decorators'.
# This allows adding behaviors (Shields, Multi-shot) without modifying the FighterJet class.
class Ship(ABC):
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
    def take_damage(self): pass # Returns True if dead, False if survived


class FighterJet(Ship):
    def __init__(self):
        self.rect = pygame.Rect(375, 500, 40, 50)
        self.lives = 3 # New: 3 Lives System

    def set_x(self, x):
        self.rect.centerx = x
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - 40))

    def take_damage(self):
        self.lives -= 1
        APILogger().log("DAMAGE", f"Hull Integrity Critical. Lives: {self.lives}")
        return self.lives <= 0


    def move(self, dx):
        self.rect.x += dx
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - 40))

    def shoot(self, bullets_list):
        # Center cannon
        b = pygame.Rect(self.rect.centerx - 2, self.rect.top, 4, 15)
        bullets_list.append(b)
        AUDIO.play_sound('shoot')
        APILogger().log("ACTION", "Cannon Fired")

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
        APILogger().log("UPGRADE", "Tactical Nuke/Rapid Fire Equipped")

    def move(self, dx): self.ship.move(dx)
    def set_x(self, x): self.ship.set_x(x)
    def take_damage(self): return self.ship.take_damage()
    def get_rect(self): return self.ship.get_rect()

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
        APILogger().log("UPGRADE", "Energy Shield Activated")

    def move(self, dx): self.ship.move(dx)
    def set_x(self, x): self.ship.set_x(x)
    def get_rect(self): return self.ship.get_rect()

    def shoot(self, bullets_list):
        self.ship.shoot(bullets_list)

    def take_damage(self):
        # Shield absorbs damage then breaks!
        APILogger().log("DECORATOR_REMOVE", "ShieldDecorator removed from Ship")
        return "BREAK_SHIELD" # Special signal to Controller to unwrap

    def draw(self, screen):
        self.ship.draw(screen)
        # Draw Blue Bubble
        pygame.draw.circle(screen, (0, 100, 255), self.ship.get_rect().center, 50, 2)

# --- STRATEGY/FACTORY: POWER UPS ---
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
            surf = GLOW_SURFACES_LIFE[pulse_idx]
            screen.blit(surf, (self.rect.centerx - surf.get_width()//2, self.rect.centery - surf.get_height()//2))
            draw_heart(screen, self.rect.centerx, self.rect.centery - 5, 20)
        else:
            surf = GLOW_SURFACES_SHIELD[pulse_idx]
            screen.blit(surf, (self.rect.centerx - surf.get_width()//2, self.rect.centery - surf.get_height()//2))
            draw_shield_emblem(screen, self.rect.centerx, self.rect.centery, 25)
