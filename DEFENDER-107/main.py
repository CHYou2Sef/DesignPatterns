# main.py
import pygame
import sys
from settings import *
from states import MenuState
from api_logger import APILogger

import asyncio

class WarGame:
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init()
        except:
            print("Warning: Sound system failed to initialize.")
            
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("API WARZONE: REST DEFENDER")
        self.clock = pygame.time.Clock()
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
            await asyncio.sleep(0) # Required for pygbag

async def main():
    game = WarGame()
    await game.run()

if __name__ == "__main__":
    asyncio.run(main())
