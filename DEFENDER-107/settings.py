# settings.py

# Screen
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Network
API_URL = "http://127.0.0.1:5000/log"
LEADERBOARD_URL = "http://127.0.0.1:5000/leaderboard"

# Theme System
CURRENT_THEME = 'DARK'  # Default theme

# Dark Theme (Original Space Theme)
DARK_THEME = {
    'BG': (5, 5, 10),              # Deep Space Black
    'STARS': (255, 255, 255),      # White Stars
    'GRID': (0, 50, 100),          # Dark Blue Grid
    'PANEL_BG': (20, 20, 40, 180), # Dark Panel
    'PANEL_BORDER': (0, 150, 255), # Blue Border
}

# Day Theme (Bright Sky Theme)
DAY_THEME = {
    'BG': (135, 206, 250),         # Sky Blue
    'STARS': (255, 255, 200),      # Bright Yellow (sun-like)
    'GRID': (100, 150, 200),       # Light Blue Grid
    'PANEL_BG': (240, 240, 255, 200), # Light Panel
    'PANEL_BORDER': (100, 100, 200),  # Purple Border
}

def get_theme_colors():
    """Returns the current theme's color dictionary"""
    return DARK_THEME if CURRENT_THEME == 'DARK' else DAY_THEME

def toggle_theme():
    """Toggle between DARK and DAY themes"""
    global CURRENT_THEME
    CURRENT_THEME = 'DAY' if CURRENT_THEME == 'DARK' else 'DARK'
    return CURRENT_THEME

# Game Colors (unchanged - used by entities)
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