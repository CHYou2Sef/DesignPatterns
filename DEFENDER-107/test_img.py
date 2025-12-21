import pygame
import os

def test_load():
    pygame.init()
    pygame.display.set_mode((1, 1))
    paths = ['img/enemy1.png', 'img/player_ship.jpg']
    for p in paths:
        print(f"Testing {p}...")
        if not os.path.exists(p):
            print(f"  FAILED: File does not exist at {os.path.abspath(p)}")
            continue
        try:
            img = pygame.image.load(p)
            print(f"  SUCCESS: Loaded {p} - size: {img.get_size()}")
        except Exception as e:
            print(f"  FAILED: Error loading {p}: {e}")
    pygame.quit()

if __name__ == "__main__":
    test_load()
