"""
Core game engine for Heavy Haul Tycoon
Handles scene management, game states, and main loop
"""
import pygame
import sys
from enum import Enum

class GameState(Enum):
    MENU = "menu"
    CONTRACT_SELECT = "contract_select"
    DRIVING = "driving"
    RESULTS = "results"
    PAUSED = "paused"

class Scene:
    """Base scene class"""
    def __init__(self, engine):
        self.engine = engine
        self.screen = engine.screen
        self.clock = engine.clock
    
    def handle_event(self, event):
        """Handle pygame events"""
        pass
    
    def update(self, dt, keys):
        """Update scene logic"""
        pass
    
    def render(self):
        """Render scene"""
        pass

class GameEngine:
    """Main game engine with scene management"""
    
    def __init__(self, width=800, height=600, title="Heavy Haul Tycoon"):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        
        # Game state
        self.running = True
        self.current_scene = None
        self.scenes = {}
        self.game_state = GameState.MENU
        
        # Game data
        self.player_data = {
            'cash': 10000,
            'fuel': 100.0,
            'truck_upgrades': {
                'engine': 1,
                'tank': 1,
                'frame': 1
            },
            'current_contract': None
        }
        
        # Fonts
        self.fonts = {
            'small': pygame.font.SysFont(None, 20),
            'medium': pygame.font.SysFont(None, 24),
            'large': pygame.font.SysFont(None, 32),
            'title': pygame.font.SysFont(None, 48)
        }
        
        # Colors
        self.colors = {
            'black': (0, 0, 0),
            'white': (255, 255, 255),
            'red': (200, 0, 0),
            'green': (0, 200, 0),
            'blue': (0, 100, 200),
            'yellow': (255, 255, 0),
            'orange': (255, 165, 0),
            'gray': (128, 128, 128),
            'dark_gray': (60, 60, 60),
            'light_gray': (200, 200, 200),
            'road_gray': (80, 80, 80),
            'grass_green': (40, 60, 40)
        }
    
    def add_scene(self, name, scene):
        """Add a scene to the engine"""
        self.scenes[name] = scene
    
    def set_scene(self, name):
        """Switch to a different scene"""
        if name in self.scenes:
            self.current_scene = self.scenes[name]
            self.game_state = GameState(name)
        else:
            print(f"Warning: Scene '{name}' not found")
    
    def get_font(self, size):
        """Get font by size name"""
        return self.fonts.get(size, self.fonts['medium'])
    
    def get_color(self, color_name):
        """Get color by name"""
        return self.colors.get(color_name, self.colors['white'])
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # ESC key behavior depends on current state
                    if self.game_state == GameState.DRIVING:
                        self.set_scene('menu')  # Pause/return to menu
                    else:
                        self.running = False
            
            # Let current scene handle events
            if self.current_scene:
                self.current_scene.handle_event(event)
    
    def update(self, dt):
        """Update game logic"""
        keys = pygame.key.get_pressed()
        
        if self.current_scene:
            self.current_scene.update(dt, keys)
    
    def render(self):
        """Render current scene"""
        if self.current_scene:
            self.current_scene.render()
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(60) / 1000.0  # 60 FPS, delta time in seconds
            
            self.handle_events()
            self.update(dt)
            self.render()
        
        pygame.quit()
        sys.exit()

# Game configuration constants
class Config:
    # Screen dimensions
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    
    # Truck physics
    TRUCK_MAX_SPEED = 4.0
    TRUCK_ACCELERATION = 0.15
    TRUCK_DECELERATION = 0.1
    TRUCK_TURN_SPEED = 2.5
    
    # Fuel system
    FUEL_CAPACITY = 100.0
    FUEL_DRAIN_RATE = 0.03
    FUEL_PRICE_PER_GALLON = 4.50
    
    # Economy
    BASE_RATE_PER_MILE = 6.00
    COLLISION_PENALTY = 250
    BRIDGE_STRIKE_PENALTY = 5000
    TOWING_FEE = 750
    
    # Contract multipliers
    WEIGHT_MULTIPLIERS = {
        'standard': 1.1,
        'oversize': 1.25,
        'superload': 1.5
    }
    
    DEADLINE_BONUS_RANGE = (1.0, 1.3)
    EARLY_DELIVERY_BONUS = 0.20
    LATE_DELIVERY_PENALTY_RANGE = (0.10, 0.50)
