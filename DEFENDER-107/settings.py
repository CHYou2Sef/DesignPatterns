# settings.py

# Screen
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Network
API_URL = "http://127.0.0.1:5000/log"
LEADERBOARD_URL = "http://127.0.0.1:5000/leaderboard"

# Cosmos Palette
COLOR_BG = (5, 5, 10)             # Deep Space Black
COLOR_PLAYER = (0, 255, 255)      # Cyan Neon
COLOR_ENEMY = (255, 50, 50)       # Red Neon
COLOR_BULLET = (255, 255, 0)      # Yellow Laser
COLOR_HUD = (0, 255, 0)           # Green Text
COLOR_STARS = (255, 255, 255)     # White Stars
COLOR_EXPLOSION = (255, 100, 0)

# Game Settings
PLAYER_SPEED = 5
ENEMY_BASE_SPEED = 0.5
HUNTER_SPEED = 1.2
HEAVY_SPEED = 0.3
MAX_HEALTH = 10
POWERUP_DURATION = 10000  # 10 seconds in milliseconds