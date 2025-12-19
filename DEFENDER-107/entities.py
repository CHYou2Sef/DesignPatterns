# entities.py
import pygame
import math
from abc import ABC, abstractmethod
from settings import *
from api_logger import APILogger

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
            s = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*COLOR_EXPLOSION, alpha), (self.radius, self.radius), self.radius)
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
        # Draw a "Drone" shape (Diamond with red eye)
        cx, cy = self.rect.centerx, self.rect.centery
        points = [(cx, cy-20), (cx+20, cy), (cx, cy+20), (cx-20, cy)]
        pygame.draw.polygon(screen, (50, 50, 50), points) # Grey Body
        pygame.draw.circle(screen, COLOR_ENEMY, (cx, cy), 8) # Red Eye
        pygame.draw.line(screen, COLOR_ENEMY, (cx, cy), (cx, cy+30), 2) # Laser sight

class EnemySquadron(GameEntity):
    def __init__(self):
        self.children = []
        self.particles = []

    def add(self, entity):
        self.children.append(entity)

    def add_explosion(self, x, y):
        self.particles.append(Particle(x, y))

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

class FighterJet(Ship):
    def __init__(self):
        self.rect = pygame.Rect(375, 500, 40, 50)

    def move(self, dx):
        self.rect.x += dx
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - 40))

    def shoot(self, bullets_list):
        # Center cannon
        b = pygame.Rect(self.rect.centerx - 2, self.rect.top, 4, 15)
        bullets_list.append(b)
        APILogger().log("ACTION", "Cannon Fired")

    def draw(self, screen):
        # Draw a cool Fighter Jet shape
        x, y = self.rect.x, self.rect.y
        # Wings
        pygame.draw.polygon(screen, (80, 80, 100), [(x, y+30), (x+40, y+30), (x+20, y)])
        # Fuselage
        pygame.draw.polygon(screen, COLOR_PLAYER, [(x+15, y+50), (x+25, y+50), (x+20, y-10)])
        # Engine Flame
        pygame.draw.polygon(screen, (255, 100, 0), [(x+18, y+50), (x+22, y+50), (x+20, y+65)])

    def get_rect(self): return self.rect

class RapidFireDecorator(Ship):
    def __init__(self, wrapped_ship):
        self.ship = wrapped_ship
        APILogger().log("UPGRADE", "Tactical Nuke/Rapid Fire Equipped")

    def move(self, dx): self.ship.move(dx)
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