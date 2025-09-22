"""
Game Constants and Configuration
"""
import pygame

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 100, 200)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (60, 60, 60)
LIGHT_GRAY = (200, 200, 200)
ROAD_GRAY = (80, 80, 80)
GRASS_GREEN = (40, 60, 40)

# Game balance constants
BASE_RATE_PER_MILE = 6.00
FUEL_DRAIN_RATE = 0.008
BRIDGE_PENALTY = 5000
REFUEL_COST = 50
STARTING_CASH = 10000
STARTING_FUEL = 100.0

# Truck physics constants
class TruckConfig:
    MAX_SPEED = 4.0
    ACCELERATION = 0.15
    DECELERATION = 0.1
    TURN_SPEED = 2.5
    REVERSE_SPEED_MULTIPLIER = 0.5

# Font initialization (call after pygame.init())
def init_fonts():
    return {
        'small': pygame.font.SysFont(None, 18),
        'normal': pygame.font.SysFont(None, 24),
        'large': pygame.font.SysFont(None, 32),
        'title': pygame.font.SysFont(None, 48)
    }
