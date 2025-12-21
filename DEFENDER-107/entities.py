# entities.py
import pygame
import math
import random
from abc import ABC, abstractmethod
from settings import *
from api_logger import APILogger

# --- ASSETS ---
try:
    SHOOT_SOUND = pygame.mixer.Sound('shoot.wav')
    EXPLOSION_SOUND = pygame.mixer.Sound('explosion.wav')
    SHOOT_SOUND.set_volume(0.4)
    EXPLOSION_SOUND.set_volume(0.5)
except:
    SHOOT_SOUND = None
    EXPLOSION_SOUND = None

# --- VISUAL HELPERS ---
def draw_heart(screen, x, y, size, color=(255, 50, 50)):
    """Procedural Heart shape"""
    # Drawing two circles and a triangle
    r = size // 2
    pygame.draw.circle(screen, color, (x - r//2, y), r//2)
    pygame.draw.circle(screen, color, (x + r//2, y), r//2)
    points = [(x - r, y + r//4), (x + r, y + r//4), (x, y + r)]
    pygame.draw.polygon(screen, color, points)

def draw_shield_emblem(screen, x, y, size, color=(50, 150, 255)):
    """Procedural Shield shape"""
    w, h = size, size
    points = [
        (x - w//2, y - h//2), (x + w//2, y - h//2),
        (x + w//2, y), (x, y + h//2), (x - w//2, y)
    ]
    pygame.draw.polygon(screen, color, points)
    pygame.draw.polygon(screen, (255, 255, 255), points, 2) # Border

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
            alpha = int((self.life / 20) * 255)
            # Dynamic Color: Yellow to Red
            color = (255, int(self.life * 10), 0)
            s = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*color, alpha), (self.radius, self.radius), self.radius)
            screen.blit(s, (self.x - self.radius, self.y - self.radius))

# --- PATTERN: COMPOSITE (Enemy Drones) ---
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
        # Pulsing Eye
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 100
        eye_color = (155 + pulse, 0, 0)
        
        # Draw a "Drone" shape with detail
        cx, cy = self.rect.centerx, self.rect.centery
        
        # Outer wing frames
        pygame.draw.line(screen, (100, 100, 100), (cx-25, cy-25), (cx+25, cy+25), 2)
        pygame.draw.line(screen, (100, 100, 100), (cx+25, cy-25), (cx-25, cy+25), 2)
        
        # Diamond body
        points = [(cx, cy-22), (cx+22, cy), (cx, cy+22), (cx-22, cy)]
        pygame.draw.polygon(screen, (30, 30, 30), points) # Dark Body
        pygame.draw.polygon(screen, (80, 80, 80), points, 2) # Light outline
        
        # Pulsing Red Eye
        pygame.draw.circle(screen, eye_color, (cx, cy), 10)
        pygame.draw.circle(screen, (255, 255, 255), (cx-3, cy-3), 3) # Highlight
        
        # Laser sight (flickering)
        if random.random() > 0.3:
            pygame.draw.line(screen, (255, 0, 0, 100), (cx, cy), (cx, cy+40), 1)

class EnemySquadron(GameEntity):
    def __init__(self):
        self.children = []
        self.particles = []

    def add(self, entity):
        self.children.append(entity)

    def add_explosion(self, x, y):
        self.particles.append(Particle(x, y))
        if EXPLOSION_SOUND: EXPLOSION_SOUND.play()

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

# --- PATTERN: DECORATOR (The Player Jet) ---
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
        if SHOOT_SOUND: SHOOT_SOUND.play()
        APILogger().log("ACTION", "Cannon Fired")

    def draw(self, screen):
        # Draw a cool Fighter Jet shape with Glow
        x, y = self.rect.x, self.rect.y
        cx, cy = self.rect.centerx, self.rect.centery
        
        # Engine Glow pulsing
        glow = abs(math.sin(pygame.time.get_ticks() * 0.01)) * 10
        pygame.draw.circle(screen, (0, 150, 255), (cx, cy + 20), 20 + glow, 1) # Hull Aura
        
        # Wings
        pygame.draw.polygon(screen, (100, 100, 120), [(x, y+30), (x+40, y+30), (x+20, y)])
        # Wing detail
        pygame.draw.line(screen, (0, 255, 255), (x+5, y+30), (x+15, y+10), 2)
        pygame.draw.line(screen, (0, 255, 255), (x+35, y+30), (x+25, y+10), 2)
        
        # Fuselage
        pygame.draw.polygon(screen, COLOR_PLAYER, [(x+14, y+50), (x+26, y+50), (x+20, y-15)])
        # Cockpit
        pygame.draw.ellipse(screen, (0, 200, 255), (x+17, y+10, 6, 15))
        
        # Engine Flame (Pulsing)
        flame_h = 15 + random.randint(0, 10)
        pygame.draw.polygon(screen, (255, 150, 0), [(x+18, y+50), (x+22, y+50), (x+20, y+50+flame_h)])
        pygame.draw.polygon(screen, (255, 255, 0), [(x+19, y+50), (x+21, y+50), (x+20, y+50+flame_h//2)])

    def get_rect(self): return self.rect

class RapidFireDecorator(Ship):
    """DECORATOR PATTERN: Adds rapid-fire capability to any Ship.
    Fires 3 bullets instead of 1, with visual energy aura effect.
    Can be stacked with other decorators for combined effects."""
    def __init__(self, wrapped_ship):
        self.ship = wrapped_ship
        self.pulse_offset = 0  # For animated visual effects
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
        # Draw Pulsing Energy Aura (CHANGE 2: Enhanced visual effects)
        self.pulse_offset += 0.15
        pulse_size = 40 + math.sin(self.pulse_offset) * 5
        alpha = int(128 + math.sin(self.pulse_offset * 2) * 127)
        aura_surf = pygame.Surface((int(pulse_size*2), int(pulse_size*2)), pygame.SRCALPHA)
        pygame.draw.circle(aura_surf, (0, 255, 255, alpha), (int(pulse_size), int(pulse_size)), int(pulse_size), 2)
        screen.blit(aura_surf, (self.ship.get_rect().centerx - int(pulse_size), self.ship.get_rect().centery - int(pulse_size)))

class ShieldDecorator(Ship):
    """DECORATOR PATTERN: Adds single-use shield protection to any Ship.
    Absorbs one hit then breaks. Visual: Blue pulsing bubble.
    Returns 'BREAK_SHIELD' signal on damage to trigger unwrapping."""
    def __init__(self, wrapped_ship):
        self.ship = wrapped_ship
        self.shield_strength = 1  # Single hit protection
        self.pulse_offset = 0  # For animated visual effects
        APILogger().log("UPGRADE", "Energy Shield Activated")

    def move(self, dx): self.ship.move(dx)
    def set_x(self, x): self.ship.set_x(x)
    def get_rect(self): return self.ship.get_rect()

    def shoot(self, bullets_list):
        self.ship.shoot(bullets_list)

    def take_damage(self):
        # Shield absorbs damage then breaks!
        APILogger().log("DEFENSE", "Shield Absorbed Impact")
        return "BREAK_SHIELD" # Special signal to Controller to unwrap

    def draw(self, screen):
        self.ship.draw(screen)
        # Draw Pulsing Blue Bubble (CHANGE 2: Enhanced visual effects)
        self.pulse_offset += 0.1
        pulse_size = 50 + math.sin(self.pulse_offset) * 3
        alpha = int(100 + math.sin(self.pulse_offset * 1.5) * 50)
        bubble_surf = pygame.Surface((int(pulse_size*2), int(pulse_size*2)), pygame.SRCALPHA)
        pygame.draw.circle(bubble_surf, (0, 100, 255, alpha), (int(pulse_size), int(pulse_size)), int(pulse_size), 3)
        screen.blit(bubble_surf, (self.ship.get_rect().centerx - int(pulse_size), self.ship.get_rect().centery - int(pulse_size)))

# --- STRATEGY/FACTORY: POWER UPS ---
# CHANGE 1: New DoubleShieldDecorator for enhanced protection
class DoubleShieldDecorator(Ship):
    """DECORATOR PATTERN: Adds double-layer shield protection to any Ship.
    Absorbs TWO hits before breaking. Visual: Dual-layer purple/blue bubble.
    Demonstrates decorator pattern flexibility with enhanced functionality."""
    def __init__(self, wrapped_ship):
        self.ship = wrapped_ship
        self.shield_strength = 2  # Double hit protection
        self.pulse_offset = 0
        APILogger().log("UPGRADE", "Double Energy Shield Activated - 2 Hits Protection")

    def move(self, dx): self.ship.move(dx)
    def set_x(self, x): self.ship.set_x(x)
    def get_rect(self): return self.ship.get_rect()

    def shoot(self, bullets_list):
        self.ship.shoot(bullets_list)

    def take_damage(self):
        self.shield_strength -= 1
        if self.shield_strength > 0:
            APILogger().log("DEFENSE", f"Double Shield Absorbed Impact - {self.shield_strength} layers remaining")
            return False  # Shield still active
        else:
            APILogger().log("DEFENSE", "Double Shield Depleted")
            return "BREAK_SHIELD"  # Signal to unwrap

    def draw(self, screen):
        self.ship.draw(screen)
        # Draw dual-layer pulsing shield (CHANGE 2: Enhanced visual effects)
        self.pulse_offset += 0.12
        
        # Outer layer (purple)
        outer_size = 55 + math.sin(self.pulse_offset) * 4
        outer_alpha = int(80 + math.sin(self.pulse_offset * 1.3) * 40)
        outer_surf = pygame.Surface((int(outer_size*2), int(outer_size*2)), pygame.SRCALPHA)
        pygame.draw.circle(outer_surf, (150, 50, 255, outer_alpha), (int(outer_size), int(outer_size)), int(outer_size), 3)
        screen.blit(outer_surf, (self.ship.get_rect().centerx - int(outer_size), self.ship.get_rect().centery - int(outer_size)))
        
        # Inner layer (blue) - only if 2 layers remain
        if self.shield_strength >= 2:
            inner_size = 45 + math.sin(self.pulse_offset + 1.5) * 3
            pygame.draw.circle(screen, (0, 150, 255), self.ship.get_rect().center, 45, 2)

# --- STRATEGY/FACTORY: POWER UPS ---
class PowerUp(GameEntity):
    def __init__(self, x, y, type_name):
        self.rect = pygame.Rect(x, y, 30, 30)
        self.type = type_name # 'SHIELD', 'DOUBLE_SHIELD', or 'LIFE'
    
    def update(self):
        self.rect.y += 3 # Fall down
        
    def draw(self, screen):
        # Glow Effect
        glow_size = 35 + math.sin(pygame.time.get_ticks() * 0.01) * 5
        glow_surf = pygame.Surface((int(glow_size*2), int(glow_size*2)), pygame.SRCALPHA)
        color = (0, 255, 0, 50) if self.type == 'LIFE' else (0, 100, 255, 50)
        pygame.draw.circle(glow_surf, color, (int(glow_size), int(glow_size)), int(glow_size))
        screen.blit(glow_surf, (self.rect.centerx - int(glow_size), self.rect.centery - int(glow_size)))

        if self.type == 'LIFE':
            draw_heart(screen, self.rect.centerx, self.rect.centery - 5, 20)
        else:
            draw_shield_emblem(screen, self.rect.centerx, self.rect.centery, 25)