import pygame
import random
from abc import ABC, abstractmethod
from settings import *
from entities import FighterJet, EnemySquadron, Drone, RapidFireDecorator, ShieldDecorator, PowerUp, draw_heart
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
            # Re-use the URL from APILogger to avoid hardcoding it in two places
            # APILogger()._url ends in /log, so we swap it for /leaderboard
            lb_url = APILogger()._url.replace("/log", "/leaderboard")
            r = requests.get(lb_url, timeout=1)
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
        
        # Cyber Grid Background
        grid_color = (0, 50, 100)
        time_offset = (pygame.time.get_ticks() // 20) % 50
        for x in range(0, SCREEN_WIDTH, 50):
            pygame.draw.line(game.screen, grid_color, (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, 50):
            pygame.draw.line(game.screen, grid_color, (0, y + time_offset), (SCREEN_WIDTH, y + time_offset), 1)

        # Neon Title
        font = pygame.font.Font(None, 80)
        # Outer Glow
        t1_glow = font.render("GALACTIC DEFENDER", True, (0, 100, 255))
        t2_glow = font.render("ENDLESS WAR", True, (255, 0, 100))
        game.screen.blit(t1_glow, (SCREEN_WIDTH//2 - t1_glow.get_width()//2 + 2, 152))
        game.screen.blit(t2_glow, (SCREEN_WIDTH//2 - t2_glow.get_width()//2 + 2, 222))
        
        t1 = font.render("GALACTIC DEFENDER", True, COLOR_PLAYER)
        t2 = font.render("ENDLESS WAR", True, COLOR_ENEMY)
        
        game.screen.blit(t1, (SCREEN_WIDTH//2 - t1.get_width()//2, 150))
        game.screen.blit(t2, (SCREEN_WIDTH//2 - t2.get_width()//2, 220))
        
        f2 = pygame.font.Font(None, 40)
        msg = f2.render("[ PRESS ENTER TO LAUNCH ]", True, (255, 255, 255))
        
        if pygame.time.get_ticks() % 1000 < 500:
            game.screen.blit(msg, (SCREEN_WIDTH//2 - msg.get_width()//2, 400))
            
        # --- Styled Leaderboard ---
        lb_panel = pygame.Surface((300, 350), pygame.SRCALPHA)
        pygame.draw.rect(lb_panel, (0, 0, 50, 150), (0, 0, 300, 350), border_radius=15)
        pygame.draw.rect(lb_panel, (0, 150, 255, 255), (0, 0, 300, 350), 2, border_radius=15)
        game.screen.blit(lb_panel, (40, 440))

        heading = f2.render("TOP PILOTS", True, (0, 255, 255))
        game.screen.blit(heading, (60, 460))
        
        y_off = 510
        font_sm = pygame.font.Font(None, 30)
        for i, entry in enumerate(self.top_scores):
            txt = f"{i+1}. {entry['username']} - {entry['score']}"
            s = font_sm.render(txt, True, (200, 200, 200))
            game.screen.blit(s, (60, y_off))
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
        self.powerups = [] # New: Powerups list
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
            
        # --- MOUSE CONTROL ---
        mx, my = pygame.mouse.get_pos()
        # Only move if mouse is inside window horizontally
        if 0 < mx < SCREEN_WIDTH:
            self.player.set_x(mx)
        
        for e in events:
            # Quit anytime
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                 game.change_state(MenuState())

            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                self.player.shoot(self.bullets)
            
            # MOUSE SHOOT
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
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
        
        if not self.squadron.children:
            self.wave += 1
            self.spawn_wave()
            
        # --- POWER UP SPAWNING ---
        if random.randint(0, 1000) < 5: # 0.5% chance per frame
            x = random.randint(50, SCREEN_WIDTH-50)
            p_type = 'SHIELD' if random.random() < 0.5 else 'LIFE'
            self.powerups.append(PowerUp(x, -50, p_type))
            
        for p in self.powerups[:]:
            p.update()
            if p.rect.y > SCREEN_HEIGHT: self.powerups.remove(p)
            # Collect
            if p.rect.colliderect(self.player.get_rect()):
                if p.type == 'SHIELD':
                     # Wrap in Shield Decorator if not already shield
                     if not isinstance(self.player, ShieldDecorator):
                         self.player = ShieldDecorator(self.player)
                elif p.type == 'LIFE':
                    # Unwrap to find base ship and add life
                    # Simple hack: we know the structure might be Decorator->Decorator->Jet
                    # But for now, let's just assume we can find 'lives' or it's on the top level object if updated properly
                    # Actually, we need to find the underlying FighterJet.
                    # Recursive search
                    curr = self.player
                    while hasattr(curr, 'ship'):
                        curr = curr.ship
                    if hasattr(curr, 'lives'):
                        curr.lives += 1
                        APILogger().log("PICKUP", f"Extra Life! Lives: {curr.lives}")
                self.powerups.remove(p)
        
        # Check Death
        player_r = self.player.get_rect()
        for d in self.squadron.children:
            # Lose if hit or enemy passes bottom
            if d.rect.colliderect(player_r) or d.rect.y > SCREEN_HEIGHT:
                result = self.player.take_damage()
                
                # If shield broke
                if result == "BREAK_SHIELD":
                    # Unwrap the shield. 
                    # If we are Shield(Jet), self.player becomes Jet.
                    # If we are Shield(Rapid(Jet)), self.player becomes Rapid(Jet).
                    # Issue: self.player might be Rapid(Shield(Jet)).
                    # Simplified assumption for this jam: P-key is rapid, pickups are shield.
                    # If top level is Shield, remove it.
                    if isinstance(self.player, ShieldDecorator):
                        self.player = self.player.ship
                        
                    # Destroy enemy that hit us
                    self.squadron.children.remove(d)
                    self.squadron.add_explosion(d.rect.centerx, d.rect.centery)
                    break
                    
                # If real damage/death
                elif result is True: # Dead
                    APILogger().log("DEATH", f"Game Over. Final Score: {self.score}")
                    if hasattr(game, 'player_name'):
                        APILogger().submit_score(game.player_name, self.score)
                    game.change_state(GameOverState(self.score, self.wave))
                else: # Took damage but alive
                    self.squadron.children.remove(d)
                    self.squadron.add_explosion(d.rect.centerx, d.rect.centery)
                    break

    def draw(self, game):
        self.stars.draw(game.screen)
        
        self.player.draw(game.screen)
        self.squadron.draw(game.screen)
        for b in self.bullets:
            pygame.draw.rect(game.screen, COLOR_BULLET, b)
        for p in self.powerups:
            p.draw(game.screen)
            
        # --- HUD (Heads Up Display) ---
        seconds = (pygame.time.get_ticks() - self.start_ticks) // 1000
        time_str = f"{seconds // 60:02}:{seconds % 60:02}"
        font = pygame.font.Font(None, 36)
        
        # Glass Panel HUD
        panel = pygame.Surface((SCREEN_WIDTH, 45), pygame.SRCALPHA)
        pygame.draw.rect(panel, (20, 20, 40, 180), (0, 0, SCREEN_WIDTH, 45))
        pygame.draw.line(panel, (0, 150, 255), (0, 44), (SCREEN_WIDTH, 44), 2)
        game.screen.blit(panel, (0, 0))
        
        # Render Stats
        txt_score = font.render(f"SCORE: {self.score}", True, (255, 255, 255))
        txt_wave = font.render(f"WAVE: {self.wave}", True, COLOR_HUD)
        txt_time = font.render(f"TIME: {time_str}", True, (255, 200, 0))
        
        game.screen.blit(txt_score, (20, 10))
        game.screen.blit(txt_wave, (350, 10))
        game.screen.blit(txt_time, (650, 10))
        
        # Draw Hearts instead of circles
        lives = 0
        curr = self.player
        while hasattr(curr, 'ship'): curr = curr.ship
        if hasattr(curr, 'lives'): lives = curr.lives
        
        for i in range(lives):
            draw_heart(game.screen, 30 + i*35, 80, 25)

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