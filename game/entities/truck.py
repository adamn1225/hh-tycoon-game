"""
Truck Entity - Player's vehicle
"""
import pygame
import math
from core.constants import TruckConfig, BLUE, LIGHT_GRAY, DARK_GRAY

class Truck:
    """Player's truck with physics, rendering, and collision detection"""
    
    def __init__(self, start_x, start_y):
        self.x = start_x
        self.y = start_y
        self.angle = 0
        self.speed = 0
        self.max_speed = TruckConfig.MAX_SPEED
        self.acceleration = TruckConfig.ACCELERATION
        self.deceleration = TruckConfig.DECELERATION
        self.turn_speed = TruckConfig.TURN_SPEED
        
    def update(self, keys, dt, speed_multiplier=1.0):
        """Update truck position and rotation based on input"""
        # Acceleration/Deceleration
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.speed = min(self.speed + self.acceleration, self.max_speed * speed_multiplier)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.speed = max(self.speed - self.acceleration, -self.max_speed * TruckConfig.REVERSE_SPEED_MULTIPLIER)
        else:
            if self.speed > 0:
                self.speed = max(0, self.speed - self.deceleration)
            elif self.speed < 0:
                self.speed = min(0, self.speed + self.deceleration)
        
        # Turning
        if abs(self.speed) > 0.1:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.angle -= self.turn_speed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.angle += self.turn_speed
        
        # Movement
        if abs(self.speed) > 0.05:
            rad = math.radians(self.angle)
            self.x += math.cos(rad) * self.speed
            self.y += math.sin(rad) * self.speed
        
        # Keep on screen but allow more space
        self.x = max(30, min(770, self.x))
        self.y = max(30, min(570, self.y))
    
    def get_rect(self):
        """Get collision rectangle for the truck"""
        return pygame.Rect(self.x - 30, self.y - 15, 60, 30)
    
    def draw(self, screen):
        """Render the truck on screen"""
        # Simplified truck drawing
        rad = math.radians(self.angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        
        # Trailer
        trailer_x = self.x - 25 * cos_a
        trailer_y = self.y - 25 * sin_a
        trailer_points = self._get_rotated_rect(trailer_x, trailer_y, 50, 15, self.angle)
        pygame.draw.polygon(screen, LIGHT_GRAY, trailer_points)
        pygame.draw.polygon(screen, DARK_GRAY, trailer_points, 2)
        
        # Cab
        cab_points = self._get_rotated_rect(self.x, self.y, 35, 20, self.angle)
        pygame.draw.polygon(screen, BLUE, cab_points)
        pygame.draw.polygon(screen, DARK_GRAY, cab_points, 2)
        
        # Windows
        front_x = self.x + 12 * cos_a
        front_y = self.y + 12 * sin_a
        window_points = self._get_rotated_rect(front_x, front_y, 8, 12, self.angle)
        pygame.draw.polygon(screen, (150, 200, 255), window_points)
    
    def _get_rotated_rect(self, center_x, center_y, width, height, angle):
        """Helper method to get rotated rectangle points"""
        rad = math.radians(angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        hw, hh = width / 2, height / 2
        corners = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
        points = []
        for cx, cy in corners:
            rx = cx * cos_a - cy * sin_a
            ry = cx * sin_a + cy * cos_a
            points.append((center_x + rx, center_y + ry))
        return points
