"""
Physics and Collision System
"""
import pygame
import math
from core.constants import BRIDGE_PENALTY

class PhysicsSystem:
    """Handles collision detection and physics interactions"""
    
    def __init__(self):
        # Road network definition
        self.roads = [
            pygame.Rect(0, 250, 800, 100),      # Main horizontal road
            pygame.Rect(150, 100, 100, 200),    # North vertical road
            pygame.Rect(550, 300, 100, 200)     # South vertical road
        ]
        
        # Hazards
        self.bridge_danger = pygame.Rect(400, 250, 80, 20)
        self.bridge_visual = pygame.Rect(400, 230, 80, 40)
    
    def is_on_road(self, truck):
        """Check if truck is on a road"""
        return any(road.collidepoint(truck.x, truck.y) for road in self.roads)
    
    def check_bridge_collision(self, game_state, truck):
        """Check for bridge collision and apply penalty"""
        truck_rect = truck.get_rect()
        if self.bridge_danger.colliderect(truck_rect):
            if not game_state.bridge_penalty_applied:
                game_state.mission_penalties.append(BRIDGE_PENALTY)
                game_state.bridge_penalty_applied = True
            return True
        return False
    
    def update_off_road_timer(self, game_state, truck, dt):
        """Update off-road warning timer"""
        if not self.is_on_road(truck) and abs(truck.speed) > 0:
            if not hasattr(game_state, 'off_road_warning_time'):
                game_state.off_road_warning_time = 0
            game_state.off_road_warning_time += dt
        else:
            game_state.off_road_warning_time = 0
    
    def check_delivery_completion(self, game_state, truck, dest_x, dest_y, dest_radius=50):
        """Check if truck has reached the destination"""
        distance_to_dest = math.sqrt((truck.x - dest_x) ** 2 + (truck.y - dest_y) ** 2)
        if distance_to_dest < dest_radius and not game_state.mission_completed:
            game_state.mission_completed = True
            return True
        return False
    
    def render_roads(self, screen):
        """Render the road network"""
        from core.constants import ROAD_GRAY, WHITE, YELLOW
        
        # Draw road surfaces
        for road in self.roads:
            pygame.draw.rect(screen, ROAD_GRAY, road)
        
        # Road markings - main road
        for x in range(0, 800, 40):
            pygame.draw.rect(screen, YELLOW, (x, 295, 20, 5))
        
        # Road markings - vertical roads
        for y in range(100, 300, 40):
            pygame.draw.rect(screen, YELLOW, (195, y, 5, 20))
        for y in range(300, 500, 40):
            pygame.draw.rect(screen, YELLOW, (595, y, 5, 20))
        
        # Road borders
        for road in self.roads:
            pygame.draw.rect(screen, WHITE, road, 2)
    
    def render_bridge(self, screen, fonts):
        """Render bridge hazard"""
        from core.constants import GRAY, DARK_GRAY, YELLOW, BLACK
        
        # Bridge structure
        pygame.draw.rect(screen, GRAY, self.bridge_visual)
        pygame.draw.rect(screen, DARK_GRAY, self.bridge_visual, 3)
        
        # Warning sign
        warning_rect = pygame.Rect(350, 200, 100, 25)
        pygame.draw.rect(screen, YELLOW, warning_rect)
        pygame.draw.rect(screen, BLACK, warning_rect, 2)
        clearance_text = fonts['small'].render("CLEARANCE 12'", True, BLACK)
        text_rect = clearance_text.get_rect(center=warning_rect.center)
        screen.blit(clearance_text, text_rect)
    
    def render_collision_warnings(self, screen, fonts, game_state, truck):
        """Render collision and warning messages"""
        from core.constants import RED, ORANGE
        
        # Bridge strike warning
        if game_state.bridge_penalty_applied:
            warning_text = fonts['normal'].render("BRIDGE STRIKE! $5000 PENALTY", True, RED)
            screen.blit(warning_text, (truck.x - 100, truck.y - 60))
        
        # Off-road warning
        if hasattr(game_state, 'off_road_warning_time') and game_state.off_road_warning_time > 2:
            offroad_text = fonts['normal'].render("OFF-ROAD: Stay on the road!", True, ORANGE)
            screen.blit(offroad_text, (truck.x - 80, truck.y - 60))
