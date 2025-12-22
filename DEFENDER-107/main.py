# main.py
import random

import pygame
import sys
from settings import *
from states import MenuState
from entities import initialize_entities
from api_logger import APILogger

# --- ASYNCIO FOR WEB ---
# We use asyncio to make the game compatible with 'pygbag' for web deployment.
# This allows the game loop to yield control to the browser's event loop.
import asyncio

class WarGame:
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init()
        except:
            print("Warning: Sound system failed to initialize.")
            
        flags = pygame.SCALED
        if FULLSCREEN:
            flags |= pygame.FULLSCREEN
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
        pygame.display.set_caption("API WARZONE: REST DEFENDER")
        self.fullscreen = FULLSCREEN
        self.clock = pygame.time.Clock()
        self.player_name = "PILOT_X" # Default Name
        
        # Explicitly initialize procedurally generated assets
        initialize_entities()
        
        self.state = MenuState()
        
        APILogger().log("SYSTEM", "War Engine Initialized")

    def change_state(self, new_state):
        """
        STATE PATTERN: Centralized state management.
        Logs the transition between GameState objects.
        """
        old_name = self.state.__class__.__name__
        new_name = new_state.__class__.__name__
        self.state = new_state
        APILogger().log("STATE_TRANSITION", f"{old_name} -> {new_name}")

    async def run(self):
        while True:
            events = pygame.event.get()
            for e in events:
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_f:
                        self.fullscreen = not self.fullscreen
                        pygame.display.toggle_fullscreen()
                        APILogger().log("SYSTEM", f"Fullscreen Toggled: {self.fullscreen}")

                if e.type == pygame.QUIT:
                    APILogger().log("SYSTEM", "Engine Shutdown")
                    APILogger().shutdown()
                    pygame.quit()
                    sys.exit()

            self.state.handle_input(events, self)
            self.state.update(self)
            self.state.draw(self)

            pygame.display.flip()
            self.clock.tick(FPS)
            # Yield control to the event loop (crucial for web/async compatibility)
            await asyncio.sleep(0) 

async def main():
    game = WarGame()
    await game.run()

if __name__ == "__main__":
    asyncio.run(main())
