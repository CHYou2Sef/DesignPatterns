import pygame
import random
import threading
from abc import ABC, abstractmethod
from settings import *
from entities import FighterJet, EnemySquadron, Drone, Hunter, Heavy, RapidFireDecorator, ShieldDecorator, PowerUp, draw_heart, Asteroid, draw_shield_emblem, AUDIO, draw_circular_timer
from api_logger import APILogger
import requests
import json

# --- COSMOS BACKGROUND GENERATOR ---
class StarField:
    def __init__(self):
        # Pre-render two layers of stars for a parallax effect
        self.layer1 = self._create_star_layer(SCREEN_WIDTH, SCREEN_HEIGHT, 50, 1)
        self.layer2 = self._create_star_layer(SCREEN_WIDTH, SCREEN_HEIGHT, 30, 2)
        self.y1 = 0
        self.y2 = 0

    def _create_star_layer(self, w, h, count, size):
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        for _ in range(count):
            x = random.randint(0, w)
            y = random.randint(0, h)
            pygame.draw.rect(surf, (200, 200, 200), (x, y, size, size))
        return surf

    def update(self):
        # Scroll layers at different speeds
        self.y1 = (self.y1 + 1) % SCREEN_HEIGHT
        self.y2 = (self.y2 + 2) % SCREEN_HEIGHT

    def draw(self, screen):
        theme = get_theme_colors()
        screen.fill(theme['BG']) # Clear screen with theme background
        # Layer 1
        screen.blit(self.layer1, (0, self.y1))
        screen.blit(self.layer1, (0, self.y1 - SCREEN_HEIGHT))
        # Layer 2
        screen.blit(self.layer2, (0, self.y2))
        screen.blit(self.layer2, (0, self.y2 - SCREEN_HEIGHT))

# --- PATTERN: STATE ---
# GameState is the base 'State' interface. 
# MenuState, WarState, etc., are 'Concrete States'.
# Transitions are handled via game.change_state() in main.py.
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
        self.menu_items = ["START MISSION", "OPTIONS", "EXIT"]
        self.selected_index = 0
        self.server_online = False
        self.fetch_leaderboard()
        AUDIO.load_sounds()
        AUDIO.play_music('music.mp3')
        # Pre-render Cyber Grid
        self.grid_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT + 50), pygame.SRCALPHA)
        grid_color = (0, 50, 100)
        for x in range(0, SCREEN_WIDTH, 50):
            pygame.draw.line(self.grid_surf, grid_color, (x, 0), (x, SCREEN_HEIGHT + 50), 1)
        for y in range(0, SCREEN_HEIGHT + 50, 50):
            pygame.draw.line(self.grid_surf, grid_color, (0, y), (SCREEN_WIDTH, y), 1)

    def fetch_leaderboard(self):
        def _fetch():
            try:
                r = requests.get(LEADERBOARD_URL, timeout=5)
                if r.status_code == 200:
                    self.top_scores = r.json()
                    self.server_online = True
                else:
                    self.server_online = False
            except:
                self.server_online = False
        
        threading.Thread(target=_fetch, daemon=True).start()

    def handle_input(self, events, game):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    # Execute selected menu item
                    if self.selected_index == 0: # START
                        game.change_state(NameInputState())
                    elif self.selected_index == 1: # OPTIONS
                        game.change_state(OptionsState(self))
                    elif self.selected_index == 2: # EXIT
                        pygame.event.post(pygame.event.Event(pygame.QUIT))
                
                if e.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.menu_items)
                if e.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.menu_items)
                
                if e.key == pygame.K_r:
                    self.fetch_leaderboard()
                
                if e.key == pygame.K_t:
                    toggle_theme()
                    APILogger().log("SYSTEM", f"Theme changed to {CURRENT_THEME} MODE")

    def update(self, game):
        self.stars.update()

    def draw(self, game):
        self.stars.draw(game.screen)
        
        # Cyber Grid Background
        theme = get_theme_colors()
        grid_color = theme['GRID']
        # Cyber Grid Background from Cache
        time_offset = (pygame.time.get_ticks() // 20) % 50
        game.screen.blit(self.grid_surf, (0, time_offset - 50))

        # Neon Title
        font = pygame.font.Font(None, 80)
        f2 = pygame.font.Font(None, 40) # Smaller font for items
        
        # Outer Glow
        t1_glow = font.render("GALACTIC DEFENDER", True, (0, 100, 255))
        t2_glow = font.render("ENDLESS WAR", True, (255, 0, 100))
        game.screen.blit(t1_glow, (SCREEN_WIDTH//2 - t1_glow.get_width()//2 + 2, 152))
        game.screen.blit(t2_glow, (SCREEN_WIDTH//2 - t2_glow.get_width()//2 + 2, 222))
        
        t1 = font.render("GALACTIC DEFENDER", True, COLOR_PLAYER)
        t2 = font.render("ENDLESS WAR", True, COLOR_ENEMY)
        
        game.screen.blit(t1, (SCREEN_WIDTH//2 - t1.get_width()//2, 150))
        game.screen.blit(t2, (SCREEN_WIDTH//2 - t2.get_width()//2, 220))
        
        if pygame.time.get_ticks() % 1000 < 500:
            msg = f2.render("[ USE ARROWS TO NAVIGATE ]", True, (200, 200, 200))
            game.screen.blit(msg, (SCREEN_WIDTH//2 - msg.get_width()//2, 380))
            
        # Draw Menu Selectors
        for i, item in enumerate(self.menu_items):
            color = (255, 255, 255) if i == self.selected_index else (100, 100, 100)
            prefix = "> " if i == self.selected_index else "  "
            txt = f2.render(prefix + item, True, color)
            game.screen.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2, 280 + i * 40))
            
        # --- Theme Indicator ---
        theme_text = f2.render(f"[T] {CURRENT_THEME} MODE", True, (150, 150, 150))
        game.screen.blit(theme_text, (SCREEN_WIDTH//2 - theme_text.get_width()//2, 500))
            
        # --- Styled Leaderboard ---
        lb_panel = pygame.Surface((300, 350), pygame.SRCALPHA)
        pygame.draw.rect(lb_panel, theme['PANEL_BG'], (0, 0, 300, 350), border_radius=15)
        pygame.draw.rect(lb_panel, (*theme['PANEL_BORDER'], 255), (0, 0, 300, 350), 2, border_radius=15)
        game.screen.blit(lb_panel, (40, 440))

        heading = f2.render("TOP PILOTS", True, (0, 255, 255))
        game.screen.blit(heading, (60, 460))
        
        # Display server status
        font_sm = pygame.font.Font(None, 30)
        status_color = (0, 255, 0) if self.server_online else (255, 50, 50)
        status_text = "[ SERVER: ONLINE ]" if self.server_online else "[ SERVER: OFFLINE ]"
        txt_status = font_sm.render(status_text, True, status_color)
        game.screen.blit(txt_status, (60, 485))
        
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
                    final_name = self.name.strip() if self.name.strip() else "PILOT_X"
                    game.player_name = final_name
                    APILogger().log("GAME_START", f"Mission Started by {final_name}")
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

# --- OPTIONS STATE ---
class OptionsState(GameState):
    """
    State for changing settings.
    Demonstrates the STATE pattern for auxiliary screens.
    """
    def __init__(self, return_state):
        self.stars = StarField()
        self.return_state = return_state
        self.sound_on = AUDIO._sound_on

    def handle_input(self, events, game):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE or e.key == pygame.K_RETURN:
                    game.change_state(self.return_state)
                if e.key == pygame.K_s:
                    self.sound_on = AUDIO.toggle_sound()

    def update(self, game): self.stars.update()

    def draw(self, game):
        self.stars.draw(game.screen)
        f = pygame.font.Font(None, 60)
        t = f.render("SETTINGS", True, (0, 255, 255))
        game.screen.blit(t, (SCREEN_WIDTH//2 - t.get_width()//2, 150))
        
        f2 = pygame.font.Font(None, 40)
        s_txt = "ON" if self.sound_on else "OFF"
        st = f2.render(f"SOUND (Press S): {s_txt}", True, (255, 255, 255))
        game.screen.blit(st, (SCREEN_WIDTH//2 - st.get_width()//2, 250))
        
        msg = f2.render("Press ESC to Return", True, (100, 100, 100))
        game.screen.blit(msg, (SCREEN_WIDTH//2 - msg.get_width()//2, 450))

# --- PAUSE STATE ---
class PauseState(GameState):
    """
    MEMENTO-ish: Freezes the previous state and overlays UI.
    Inherits previous state behavior without updating it.
    """
    def __init__(self, war_state):
        self.previous_state = war_state
        self.pause_start = pygame.time.get_ticks()

    def handle_input(self, events, game):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE or e.key == pygame.K_p:
                    # Calculate duration of this pause session and add it to state
                    duration = pygame.time.get_ticks() - self.pause_start
                    self.previous_state.paused_duration += duration
                    game.change_state(self.previous_state)
                
                if e.key == pygame.K_m:
                    game.change_state(MenuState())

    def update(self, game): pass # Logic frozen

    def draw(self, game):
        # Draw background game state first
        self.previous_state.draw(game)
        
        # Overlay darkening
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180)) # Slightly darker
        game.screen.blit(overlay, (0,0))
        
        font = pygame.font.Font(None, 100)
        t = font.render("PAUSED", True, (255, 255, 255))
        game.screen.blit(t, (SCREEN_WIDTH//2 - t.get_width()//2, SCREEN_HEIGHT//2 - 50))
        
        f2 = pygame.font.Font(None, 40)
        msg = f2.render("Press P to Resume | Press M for Menu", True, (200, 200, 200))
        game.screen.blit(msg, (SCREEN_WIDTH//2 - msg.get_width()//2, SCREEN_HEIGHT//2 + 50))

# --- PLAYING STATE (ENDLESS) ---
class WarState(GameState):
    def __init__(self):
        self.stars = StarField()
        self.squadron = EnemySquadron()
        self.player = FighterJet()
        self.bullets = []
        self.powerups = []
        self.obstacles = [] # Asteroids
        self.decorated = False
        self.player_moving = False
        
        # Scoreboard & Timer Stats
        self.start_ticks = pygame.time.get_ticks()
        self.paused_duration = 0
        self.score = 0
        self.wave = 1
        
        # Wave Notification System
        self.wave_notification = None  # Text to display
        self.wave_notification_timer = 0  # Duration to show notification
        
        # Initial Wave
        self.spawn_wave()
        
        # Pre-render HUD Panel
        self.hud_panel = pygame.Surface((SCREEN_WIDTH, 45), pygame.SRCALPHA)
        pygame.draw.rect(self.hud_panel, (20, 20, 40, 180), (0, 0, SCREEN_WIDTH, 45))
        pygame.draw.line(self.hud_panel, (0, 150, 255), (0, 44), (SCREEN_WIDTH, 44), 2)

    def spawn_wave(self):
        # Show wave notification (except for wave 1)
        if self.wave > 1:
            self.wave_notification = f"WAVE {self.wave}"
            self.wave_notification_timer = 120  # Show for 2 seconds (120 frames at 60 FPS)
        
        #Enemy wave Loggs
        APILogger().log("GAME", f"Wave {self.wave} Spawning")
        # Increase enemy count every wave
        count = 3 + int(self.wave * 1.5)
        speed_boost = min(3.0, self.wave * 0.2) # Cap speed so it's not impossible
        
        #Spawn enemies based on wave
        for i in range(count):
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(-200, -50)
            
            roll = random.random()
            if self.wave < 3:
                # Only Drones in early waves
                self.squadron.add(Drone(x, y, speed_mod=speed_boost))
            elif self.wave < 6:
                # Intro Hunters
                if roll < 0.7:
                    self.squadron.add(Drone(x, y, speed_mod=speed_boost))
                else:
                    self.squadron.add(Hunter(x, y, speed_mod=speed_boost))
            else:
                # All types in later waves
                if roll < 0.5:
                    self.squadron.add(Drone(x, y, speed_mod=speed_boost))
                elif roll < 0.8:
                    self.squadron.add(Hunter(x, y, speed_mod=speed_boost))
                else:
                    self.squadron.add(Heavy(x, y, speed_mod=speed_boost))

    #Input handling
    def handle_input(self, events, game):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: self.player.move(-PLAYER_SPEED)
        if keys[pygame.K_RIGHT]: self.player.move(PLAYER_SPEED)
            
        mx, my = pygame.mouse.get_pos()
        # Only move if mouse is inside window horizontally
        moving_now = False
        if 0 < mx < SCREEN_WIDTH:
            self.player.set_x(mx)
            # Check if actually moved (roughly)
            moving_now = True
            
        # Log character state change: Idle <-> Moving
        if moving_now != self.player_moving:
            self.player_moving = moving_now
            state_label = "Moving" if moving_now else "Idle"
            APILogger().log("CHARACTER_STATE", f"Pilot -> {state_label}")
        
        for e in events:
            # Quit anytime
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                 game.change_state(MenuState())

            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                self.player.shoot(self.bullets)
            
            # --- PAUSE TRIGGER ---
            if e.type == pygame.KEYDOWN and (e.key == pygame.K_ESCAPE or e.key == pygame.K_p):
                game.change_state(PauseState(self))
            
            # MOUSE SHOOT
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                self.player.shoot(self.bullets)

    def update(self, game):
        self.stars.update()
        self.squadron.update()
        
        # Update wave notification timer
        if self.wave_notification_timer > 0:
            self.wave_notification_timer -= 1
            if self.wave_notification_timer == 0:
                self.wave_notification = None
        
        # Bullets
        # Update player (handles timed effects)
        p_status = self.player.update()
        if p_status == "EXPIRED":
            # Revert to normal FighterJet as requested
            self.player = self.player.get_base_ship()
            self.decorated = False

        self._update_projectiles()
        self._handle_spawn_logic(game)
        self._handle_powerups()
        self._handle_collisions(game)

    def _update_projectiles(self):
        for b in self.bullets[:]:
            b.y -= 10
            if b.y < 0: 
                self.bullets.remove(b)
                continue
            
            # Drone/Hunter/Heavy Collision
            for enemy in self.squadron.children[:]:
                if b.colliderect(enemy.rect):
                    # Check HP
                    enemy.hp -= 1
                    if enemy.hp <= 0:
                        self.squadron.add_explosion(enemy.rect.centerx, enemy.rect.centery)
                        self.squadron.children.remove(enemy)
                        self.score += 100 * self.wave
                        APILogger().log("ENTITY_DESTROY", f"{enemy.__class__.__name__} destroyed. Score: {self.score}")
                    
                    if b in self.bullets: self.bullets.remove(b)
                    return # Bullet gone

            # Asteroid Collision
            for ast in self.obstacles[:]:
                if b.colliderect(ast.rect):
                    self.squadron.add_explosion(ast.rect.centerx, ast.rect.centery)
                    self.obstacles.remove(ast)
                    if b in self.bullets: self.bullets.remove(b)
                    self.score += 50
                    return

    def _handle_spawn_logic(self, game):
        # Wave complete?
        if not self.squadron.children:
            self.wave += 1
            if self.wave > 10:
                APILogger().log("RESULT", "Victory Reached Wave 10+")
                if hasattr(game, 'player_name'):
                    APILogger().submit_score(game.player_name, self.score)
                game.change_state(VictoryState(self.score))
                return
            self.spawn_wave()
        
        # Obstacles
        for ast in self.obstacles[:]:
            ast.update()
            if ast.rect.y > SCREEN_HEIGHT: self.obstacles.remove(ast)
        
        if random.randint(0, 1000) < 10:
             self.obstacles.append(Asteroid(random.randint(0, SCREEN_WIDTH), -50))

        # PowerUp spawning
        if random.randint(0, 1000) < 8:
            x = random.randint(50, SCREEN_WIDTH-50)
            roll = random.random()
            
            # 1- the 3 shoots don't appears in the 3 first waves
            if self.wave < 3:
                p_type = 'SHIELD' if roll < 0.5 else 'LIFE'
            else:
                p_type = 'SHIELD' if roll < 0.4 else 'LIFE' if roll < 0.7 else 'RAPID'
            
            self.powerups.append(PowerUp(x, -50, p_type))

    def _handle_powerups(self):
        for p in self.powerups[:]:
            p.update()
            if p.rect.y > SCREEN_HEIGHT: 
                self.powerups.remove(p)
                continue

            if p.rect.colliderect(self.player.get_rect()):
                APILogger().log("PICKUP", f"Collected {p.type} PowerUp")
                if p.type == 'SHIELD':
                     if not self.player.has_decorator(ShieldDecorator):
                          self.player = ShieldDecorator(self.player)
                elif p.type == 'LIFE':
                    base = self.player.get_base_ship()
                    if base.lives < MAX_HEALTH:
                        base.lives += 1
                    else:
                        APILogger().log("STATUS", "Health at CAP (10)")
                elif p.type == 'RAPID':
                    # Wave Lock: Only unlock after Wave 3
                    if self.wave >= 3:
                        if not self.player.has_decorator(RapidFireDecorator):
                             self.player = RapidFireDecorator(self.player)
                             self.decorated = True
                    else:
                        APILogger().log("STATUS", "Rapid Fire locked until Wave 3")
                self.powerups.remove(p)

    def _handle_collisions(self, game):
        player_r = self.player.get_rect()
        
        # Asteroids
        for ast in self.obstacles[:]:
            if ast.rect.colliderect(player_r):
                self.obstacles.remove(ast)
                self.squadron.add_explosion(ast.rect.centerx, ast.rect.centery)
                if self.player.take_damage() is True:
                     self._trigger_game_over(game)
                     return

        # Drones
        for d in self.squadron.children[:]:
            if d.rect.colliderect(player_r) or d.rect.y > SCREEN_HEIGHT:
                result = self.player.take_damage()
                
                if result == "BREAK_SHIELD":
                    self.player = self.player.remove_decorator(ShieldDecorator)
                    self.squadron.children.remove(d)
                    self.squadron.add_explosion(d.rect.centerx, d.rect.centery)
                elif result is True: # Death
                    self._trigger_game_over(game)
                    return
                else: # Tanked it (or just damage)
                    self.squadron.children.remove(d)
                    self.squadron.add_explosion(d.rect.centerx, d.rect.centery)

    def _trigger_game_over(self, game):
        APILogger().log("DEATH", f"Game Over. Final Score: {self.score}")
        if hasattr(game, 'player_name'):
            APILogger().submit_score(game.player_name, self.score)
        game.change_state(GameOverState(self.score, self.wave))

    def draw(self, game):
        self.stars.draw(game.screen)
        
        self.player.draw(game.screen)
        self.squadron.draw(game.screen)
        for ast in self.obstacles: 
            ast.draw(game.screen)
        for b in self.bullets:
            pygame.draw.rect(game.screen, COLOR_BULLET, b)
        for p in self.powerups:
            p.draw(game.screen)
            
        # --- HUD (Heads Up Display) ---
        # If we are drawing from PauseState, we need to show the time frozen at pause_start
        current_tick = pygame.time.get_ticks()
        # Find if we are currently being drawn by a PauseState or if we are the active state
        # A bit hacky but works for this architecture: check game.state
        if game.state.__class__.__name__ == "PauseState" and hasattr(game.state, 'pause_start'):
            current_tick = game.state.pause_start

        seconds = (current_tick - self.start_ticks - self.paused_duration) // 1000
        time_str = f"{seconds // 60:02}:{seconds % 60:02}"
        font = pygame.font.Font(None, 36)
        
        # Glass Panel HUD from Cache
        game.screen.blit(self.hud_panel, (0, 0))
        
        # Render Stats
        pilot_name = getattr(game, 'player_name', "Unknown")
        txt_pilot = font.render(f"PILOT: {pilot_name}", True, (0, 255, 255))
        txt_score = font.render(f"SCORE: {self.score}", True, (255, 255, 255))
        txt_wave = font.render(f"WAVE: {self.wave}", True, COLOR_HUD)
        txt_time = font.render(f"TIME: {time_str}", True, (255, 200, 0))
        
        game.screen.blit(txt_pilot, (15, 10))
        game.screen.blit(txt_score, (250, 10))
        game.screen.blit(txt_wave, (550, 10))
        game.screen.blit(txt_time, (850, 10))
        
        # Draw Hearts instead of circles
        base = self.player.get_base_ship()
        lives = base.lives
        
        for i in range(lives):
            draw_heart(game.screen, 30 + i*35, 80, 25)
        
        # --- WAVE NOTIFICATION ---
        if self.wave_notification and self.wave_notification_timer > 0:
            # Calculate alpha for fade effect
            if self.wave_notification_timer > 100:
                alpha = min(255, (120 - self.wave_notification_timer) * 12)  # Fade in
            elif self.wave_notification_timer < 20:
                alpha = self.wave_notification_timer * 12  # Fade out
            else:
                alpha = 255  # Full opacity
            
            # Create notification surface
            notif_font = pygame.font.Font(None, 100)
            notif_text = notif_font.render(self.wave_notification, True, (255, 255, 0))
            
            # Create semi-transparent surface
            notif_surface = pygame.Surface((notif_text.get_width() + 60, notif_text.get_height() + 40), pygame.SRCALPHA)
            pygame.draw.rect(notif_surface, (0, 0, 0, min(200, alpha)), (0, 0, notif_surface.get_width(), notif_surface.get_height()), border_radius=20)
            pygame.draw.rect(notif_surface, (255, 255, 0, alpha), (0, 0, notif_surface.get_width(), notif_surface.get_height()), 3, border_radius=20)
            
            # Blit text onto notification surface
            notif_text.set_alpha(alpha)
            notif_surface.blit(notif_text, (30, 20))
            
            # Center on screen
            x_pos = SCREEN_WIDTH // 2 - notif_surface.get_width() // 2
            y_pos = SCREEN_HEIGHT // 2 - notif_surface.get_height() // 2
            game.screen.blit(notif_surface, (x_pos, y_pos))
            
        # --- ACTIVE POWER-UPS ICONS ---
        # Show Shield/Rapid icons next to score if active with Circular Timers
        icon_x = 180
        
        # Shield
        if self.player.has_decorator(ShieldDecorator):
            # Find the decorator in the stack to get its time
            curr = self.player
            while curr and not isinstance(curr, ShieldDecorator):
                curr = getattr(curr, 'ship', None)
            
            if curr:
                draw_shield_emblem(game.screen, icon_x, 25, 20)
                # Progress for timer
                elapsed = pygame.time.get_ticks() - curr.start_time
                progress = max(0, (curr.duration - elapsed) / curr.duration)
                draw_circular_timer(game.screen, (icon_x, 25), progress, (0, 200, 255))
                icon_x += 40
        
        # Rapid Fire (3 shoots)
        if self.decorated:
            curr = self.player
            while curr and not isinstance(curr, RapidFireDecorator):
                curr = getattr(curr, 'ship', None)
            
            if curr:
                # Use a small rect or icon for Rapid Fire
                pygame.draw.rect(game.screen, (255, 255, 0), (icon_x - 5, 15, 10, 20))
                elapsed = pygame.time.get_ticks() - curr.start_time
                progress = max(0, (curr.duration - elapsed) / curr.duration)
                draw_circular_timer(game.screen, (icon_x, 25), progress, (255, 255, 0))
                icon_x += 40

# --- VICTORY STATE ---
class VictoryState(GameState):
    def __init__(self, score):
        self.score = score
        self.stars = StarField()

    def handle_input(self, events, game):
        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                game.change_state(MenuState())

    def update(self, game): self.stars.update()

    def draw(self, game):
        self.stars.draw(game.screen)
        f = pygame.font.Font(None, 80)
        t = f.render("MISSION ACCOMPLISHED", True, (0, 255, 0))
        game.screen.blit(t, (SCREEN_WIDTH//2 - t.get_width()//2, 150))
        
        f2 = pygame.font.Font(None, 40)
        st = f2.render(f"FINAL SCORE: {self.score}", True, (255, 255, 255))
        game.screen.blit(st, (SCREEN_WIDTH//2 - st.get_width()//2, 250))
        
        msg = f2.render("The galaxy is safe... for now. Press ENTER", True, (200, 200, 200))
        game.screen.blit(msg, (SCREEN_WIDTH//2 - msg.get_width()//2, 450))

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