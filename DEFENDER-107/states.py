import pygame
import random
from abc import ABC, abstractmethod
from settings import *
from entities import FighterJet, EnemySquadron, Drone, RapidFireDecorator
from api_logger import APILogger
import requests
import json

# --- COSMOS BACKGROUND GENERATOR ---
class StarField:
    def __init__(self):
        self.stars = []
        # Create 100 random stars: [x, y, speed, size]
        for _ in range(100):
            self.stars.append([
                random.randint(0, SCREEN_WIDTH),
                random.randint(0, SCREEN_HEIGHT),
                random.uniform(0.5, 3.0), # Speed
                random.randint(1, 3)      # Size
            ])

    def update(self):
        for star in self.stars:
            star[1] += star[2] # Move down (y + speed)
            # Reset to top if it goes off screen
            if star[1] > SCREEN_HEIGHT:
                star[1] = 0
                star[0] = random.randint(0, SCREEN_WIDTH)

    def draw(self, screen):
        screen.fill(COLOR_BG) # Clear screen with dark space color
        for star in self.stars:
            pygame.draw.circle(screen, COLOR_STARS, (int(star[0]), int(star[1])), star[3])

# --- STATE PATTERN BASE ---
class GameState(ABC):
    @abstractmethod
    def handle_input(self, events, game): pass
    @abstractmethod
    def update(self, game): pass
    @abstractmethod
    def draw(self, game): pass

# --- MENU STATE ---
class MenuState(GameState):
    def __init__(self):
        self.stars = StarField()
        self.top_scores = []
        self.fetch_leaderboard()

    def fetch_leaderboard(self):
        # Fetch in a separate thread optionally, but for simplicity we'll try a quick timeout here
        # or just do it blocking for a moment (it's a menu)
        try:
            r = requests.get("http://127.0.0.1:5000/leaderboard", timeout=1)
            if r.status_code == 200:
                self.top_scores = r.json()
        except:
            self.top_scores = []

    def handle_input(self, events, game):
        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                # game.change_state(WarState()) -> Old way
                game.change_state(NameInputState()) # New way
            if e.type == pygame.KEYDOWN and e.key == pygame.K_r:
                self.fetch_leaderboard()

    def update(self, game):
        self.stars.update()

    def draw(self, game):
        self.stars.draw(game.screen)
        
        # Neon Title
        font = pygame.font.Font(None, 80)
        t1 = font.render("GALACTIC DEFENDER", True, COLOR_PLAYER)
        t2 = font.render("ENDLESS WAR", True, COLOR_ENEMY)
        
        # Centering text
        game.screen.blit(t1, (SCREEN_WIDTH//2 - t1.get_width()//2, 150))
        game.screen.blit(t2, (SCREEN_WIDTH//2 - t2.get_width()//2, 220))
        
        f2 = pygame.font.Font(None, 40)
        msg = f2.render("[ PRESS ENTER TO LAUNCH ]", True, (255, 255, 255))
        
        # blinking effect
        if pygame.time.get_ticks() % 1000 < 500:
            game.screen.blit(msg, (SCREEN_WIDTH//2 - msg.get_width()//2, 400))
            
        # Draw Leaderboard
        heading = f2.render("TOP PILOTS", True, (0, 255, 255))
        game.screen.blit(heading, (50, 450))
        
        y_off = 500
        font_sm = pygame.font.Font(None, 30)
        for i, entry in enumerate(self.top_scores):
            txt = f"{i+1}. {entry['username']} - {entry['score']}"
            s = font_sm.render(txt, True, (200, 200, 200))
            game.screen.blit(s, (50, y_off))
            y_off += 30

# --- NAME INPUT STATE ---
class NameInputState(GameState):
    def __init__(self):
        self.stars = StarField()
        self.name = ""

    def handle_input(self, events, game):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    if self.name.strip():
                        game.player_name = self.name # Save to global game object
                        APILogger().log("STATE", f"Mission Started by {self.name}")
                        game.change_state(WarState())
                elif e.key == pygame.K_BACKSPACE:
                    self.name = self.name[:-1]
                else:
                    # Limit length
                    if len(self.name) < 10 and e.unicode.isalnum():
                        self.name += e.unicode

    def update(self, game):
        self.stars.update()

    def draw(self, game):
        self.stars.draw(game.screen)
        
        font = pygame.font.Font(None, 60)
        t = font.render("ENTER PILOT NAME:", True, (255, 255, 0))
        game.screen.blit(t, (SCREEN_WIDTH//2 - t.get_width()//2, 200))
        
        name_t = font.render(self.name + "_", True, (255, 255, 255))
        game.screen.blit(name_t, (SCREEN_WIDTH//2 - name_t.get_width()//2, 300))

# --- PLAYING STATE (ENDLESS) ---
class WarState(GameState):
    def __init__(self):
        self.stars = StarField()
        self.squadron = EnemySquadron()
        self.player = FighterJet()
        self.bullets = []
        self.decorated = False
        
        # Scoreboard & Timer Stats
        self.start_ticks = pygame.time.get_ticks()
        self.score = 0
        self.wave = 1
        
        # Initial Wave
        self.spawn_wave()

    def spawn_wave(self):
        APILogger().log("GAME", f"Wave {self.wave} Spawning")
        # Increase enemy count every wave
        count = 3 + int(self.wave * 1.5)
        speed_boost = min(3.0, self.wave * 0.2) # Cap speed so it's not impossible
        
        for i in range(count):
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(-200, -50) # Spawn above screen
            self.squadron.add(Drone(x, y, speed_mod=speed_boost))

    def handle_input(self, events, game):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: self.player.move(-PLAYER_SPEED)
        if keys[pygame.K_RIGHT]: self.player.move(PLAYER_SPEED)
        if keys[pygame.K_p] and not self.decorated:
            self.player = RapidFireDecorator(self.player)
            self.decorated = True
        
        for e in events:
            # Quit anytime
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                 game.change_state(MenuState())

            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                self.player.shoot(self.bullets)

    def update(self, game):
        self.stars.update()
        self.squadron.update()
        
        # Bullets
        for b in self.bullets[:]:
            b.y -= 10
            if b.y < 0: self.bullets.remove(b)
            
            # Collision
            for drone in self.squadron.children[:]:
                if b.colliderect(drone.rect):
                    self.squadron.add_explosion(drone.rect.centerx, drone.rect.centery)
                    self.squadron.children.remove(drone)
                    if b in self.bullets: self.bullets.remove(b)
                    
                    self.score += 100 * self.wave
                    APILogger().log("KILL", f"Enemy Down. Score: {self.score}")
                    break

        # --- ENDLESS MODE LOGIC ---
        # If all enemies dead, spawn next wave immediately
        if not self.squadron.children:
            self.wave += 1
            self.spawn_wave()
        
        # Check Death
        player_r = self.player.get_rect()
        for d in self.squadron.children:
            # Lose if hit or enemy passes bottom
            if d.rect.colliderect(player_r) or d.rect.y > SCREEN_HEIGHT:
                APILogger().log("DEATH", f"Game Over. Final Score: {self.score}")
                # Submit score if player_name exists
                if hasattr(game, 'player_name'):
                    APILogger().submit_score(game.player_name, self.score)
                    
                game.change_state(GameOverState(self.score, self.wave))

    def draw(self, game):
        self.stars.draw(game.screen)
        
        self.player.draw(game.screen)
        self.squadron.draw(game.screen)
        for b in self.bullets:
            pygame.draw.rect(game.screen, COLOR_BULLET, b)
            
        # --- HUD (Heads Up Display) ---
        # 1. Timer
        seconds = (pygame.time.get_ticks() - self.start_ticks) // 1000
        time_str = f"{seconds // 60:02}:{seconds % 60:02}"
        
        font = pygame.font.Font(None, 36)
        
        # Draw Top Bar Background
        pygame.draw.rect(game.screen, (20, 20, 40), (0, 0, SCREEN_WIDTH, 40))
        pygame.draw.line(game.screen, COLOR_PLAYER, (0, 40), (SCREEN_WIDTH, 40), 2)
        
        # Render Stats
        txt_score = font.render(f"SCORE: {self.score}", True, (255, 255, 255))
        txt_wave = font.render(f"WAVE: {self.wave}", True, COLOR_HUD)
        txt_time = font.render(f"TIME: {time_str}", True, (255, 200, 0))
        
        game.screen.blit(txt_score, (20, 10))
        game.screen.blit(txt_wave, (350, 10))
        game.screen.blit(txt_time, (650, 10))

# --- GAME OVER STATE ---
class GameOverState(GameState):
    def __init__(self, score, wave):
        self.score = score
        self.wave = wave
        self.stars = StarField()

    def handle_input(self, events, game):
        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                game.change_state(MenuState())

    def update(self, game):
        self.stars.update()

    def draw(self, game):
        self.stars.draw(game.screen)
        
        font = pygame.font.Font(None, 80)
        t = font.render("GAME OVER", True, (255, 0, 0))
        game.screen.blit(t, (SCREEN_WIDTH//2 - t.get_width()//2, 150))
        
        f2 = pygame.font.Font(None, 50)
        s_txt = f2.render(f"FINAL SCORE: {self.score}", True, (255, 255, 255))
        w_txt = f2.render(f"WAVES SURVIVED: {self.wave}", True, (0, 255, 0))
        
        game.screen.blit(s_txt, (SCREEN_WIDTH//2 - s_txt.get_width()//2, 250))
        game.screen.blit(w_txt, (SCREEN_WIDTH//2 - w_txt.get_width()//2, 300))
        
        f3 = pygame.font.Font(None, 30)
        msg = f3.render("Press ENTER to Try Again", True, (150, 150, 150))
        game.screen.blit(msg, (SCREEN_WIDTH//2 - msg.get_width()//2, 450))