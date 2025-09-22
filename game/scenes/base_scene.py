"""
Base Scene Class
"""
import pygame

class BaseScene:
    """Abstract base class for game scenes"""
    
    def __init__(self, fonts):
        self.fonts = fonts
    
    def handle_event(self, event, game_state):
        """Handle pygame events - override in subclasses"""
        pass
    
    def update(self, dt, game_state):
        """Update scene logic - override in subclasses"""
        pass
    
    def render(self, screen, game_state):
        """Render scene - override in subclasses"""
        pass
