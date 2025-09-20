"""
Driving mechanics and environment systems
Handles roads, collision detection, and vehicle physics
"""
import pygame
import math

class Road:
    """Road segment with collision detection"""
    def __init__(self, x, y, width, height, road_type="highway"):
        self.rect = pygame.Rect(x, y, width, height)
        self.road_type = road_type
        self.surface_type = "asphalt"  # asphalt, gravel, dirt
        
    def is_point_on_road(self, x, y):
        """Check if a point is on this road"""
        return self.rect.collidepoint(x, y)
    
    def render(self, screen, colors):
        """Render the road"""
        # Road surface
        pygame.draw.rect(screen, colors['road_gray'], self.rect)
        
        # Road markings
        if self.road_type == "highway":
            # Center lines
            line_y = self.rect.centery
            for x in range(self.rect.left, self.rect.right, 40):
                line_rect = pygame.Rect(x, line_y - 2, 20, 4)
                pygame.draw.rect(screen, colors['yellow'], line_rect)
        
        # Road edges
        pygame.draw.line(screen, colors['white'], 
                        (self.rect.left, self.rect.top), 
                        (self.rect.right, self.rect.top), 2)
        pygame.draw.line(screen, colors['white'], 
                        (self.rect.left, self.rect.bottom), 
                        (self.rect.right, self.rect.bottom), 2)

class Bridge:
    """Bridge obstacle with clearance checking"""
    def __init__(self, x, y, width, clearance_height=12):
        self.rect = pygame.Rect(x, y, width, 40)
        self.clearance_height = clearance_height
        self.collision_zone = pygame.Rect(x, y + 20, width, 20)  # Bottom part
        
    def check_collision(self, truck_rect, truck_height=15):
        """Check if truck hits bridge (too tall)"""
        if self.collision_zone.colliderect(truck_rect):
            return truck_height > self.clearance_height
        return False
    
    def render(self, screen, colors, font):
        """Render bridge with clearance warning"""
        # Bridge structure
        pygame.draw.rect(screen, colors['gray'], self.rect)
        pygame.draw.rect(screen, colors['dark_gray'], self.rect, 3)
        
        # Clearance warning sign
        sign_rect = pygame.Rect(self.rect.x - 50, self.rect.y - 30, 100, 25)
        pygame.draw.rect(screen, colors['yellow'], sign_rect)
        pygame.draw.rect(screen, colors['black'], sign_rect, 2)
        
        clearance_text = font.render(f"CLEARANCE {self.clearance_height}'", True, colors['black'])
        text_rect = clearance_text.get_rect(center=sign_rect.center)
        screen.blit(clearance_text, text_rect)
        
        # Danger zone highlight
        danger_rect = pygame.Rect(self.rect.x, self.rect.bottom - 5, self.rect.width, 25)
        pygame.draw.rect(screen, (255, 0, 0, 50), danger_rect)

class FuelStation:
    """Fuel station for refueling"""
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 80, 60)
        self.interaction_zone = pygame.Rect(x - 20, y - 20, 120, 100)
        self.fuel_price = 4.50  # per gallon
        
    def can_refuel(self, truck_rect):
        """Check if truck is in refueling range"""
        return self.interaction_zone.colliderect(truck_rect)
    
    def render(self, screen, colors, font):
        """Render fuel station"""
        # Station building
        pygame.draw.rect(screen, colors['light_gray'], self.rect)
        pygame.draw.rect(screen, colors['dark_gray'], self.rect, 2)
        
        # Fuel pumps
        pump1 = pygame.Rect(self.rect.x + 10, self.rect.bottom, 15, 20)
        pump2 = pygame.Rect(self.rect.x + 55, self.rect.bottom, 15, 20)
        pygame.draw.rect(screen, colors['red'], pump1)
        pygame.draw.rect(screen, colors['red'], pump2)
        
        # Price sign
        price_text = font.render(f"${self.fuel_price:.2f}/gal", True, colors['white'])
        screen.blit(price_text, (self.rect.x, self.rect.y - 20))
        
        # Interaction zone (when truck is nearby)
        # This would be highlighted when truck approaches

class Environment:
    """Game environment with roads, bridges, and hazards"""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.roads = []
        self.bridges = []
        self.fuel_stations = []
        self.off_road_penalty = 0.5  # Speed multiplier when off-road
        
        self._create_default_environment()
    
    def _create_default_environment(self):
        """Create the default level environment"""
        # Main highway (horizontal)
        main_road = Road(0, 250, self.width, 100, "highway")
        self.roads.append(main_road)
        
        # Side roads
        side_road1 = Road(150, 150, 100, 200, "street")
        side_road2 = Road(550, 150, 100, 200, "street")
        self.roads.append(side_road1)
        self.roads.append(side_road2)
        
        # Bridges
        low_bridge = Bridge(400, 230, 80, 12)  # Low clearance
        self.bridges.append(low_bridge)
        
        # Fuel stations
        station1 = FuelStation(100, 180)
        station2 = FuelStation(650, 180)
        self.fuel_stations.append(station1)
        self.fuel_stations.append(station2)
    
    def is_on_road(self, x, y):
        """Check if coordinates are on any road"""
        for road in self.roads:
            if road.is_point_on_road(x, y):
                return True
        return False
    
    def check_bridge_collisions(self, truck_rect, truck_height=15):
        """Check for bridge strikes"""
        for bridge in self.bridges:
            if bridge.check_collision(truck_rect, truck_height):
                return bridge
        return None
    
    def get_nearby_fuel_station(self, truck_rect):
        """Get fuel station if truck is in range"""
        for station in self.fuel_stations:
            if station.can_refuel(truck_rect):
                return station
        return None
    
    def get_speed_multiplier(self, truck_x, truck_y):
        """Get speed multiplier based on surface"""
        if self.is_on_road(truck_x, truck_y):
            return 1.0  # Normal speed on road
        else:
            return self.off_road_penalty  # Slower off-road
    
    def render(self, screen, colors, font):
        """Render the environment"""
        # Background (grass)
        screen.fill(colors['grass_green'])
        
        # Roads
        for road in self.roads:
            road.render(screen, colors)
        
        # Fuel stations
        for station in self.fuel_stations:
            station.render(screen, colors, font)
        
        # Bridges (render last so they appear on top)
        for bridge in self.bridges:
            bridge.render(screen, colors, font)

class DeliveryZone:
    """Destination zone for deliveries"""
    def __init__(self, x, y, radius=50):
        self.x = x
        self.y = y
        self.radius = radius
        self.rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
        self.completed = False
        self.flash_timer = 0
        
    def check_delivery(self, truck_x, truck_y):
        """Check if truck has reached delivery zone"""
        distance = math.sqrt((truck_x - self.x) ** 2 + (truck_y - self.y) ** 2)
        return distance <= self.radius
    
    def update(self, dt):
        """Update delivery zone animations"""
        self.flash_timer += dt * 3
    
    def render(self, screen, colors, font):
        """Render delivery destination"""
        # Pulsing circle effect
        pulse = abs(math.sin(self.flash_timer))
        inner_radius = int(self.radius * 0.7 + pulse * 10)
        outer_radius = int(self.radius)
        
        # Outer ring
        pygame.draw.circle(screen, colors['green'], (int(self.x), int(self.y)), outer_radius, 3)
        
        # Inner circle
        pygame.draw.circle(screen, (0, 255, 0, 100), (int(self.x), int(self.y)), inner_radius)
        
        # Destination marker
        dest_text = font.render("DELIVERY", True, colors['white'])
        text_rect = dest_text.get_rect(center=(self.x, self.y - self.radius - 20))
        
        # Text background
        bg_rect = text_rect.inflate(10, 5)
        pygame.draw.rect(screen, colors['black'], bg_rect, border_radius=3)
        screen.blit(dest_text, text_rect)

class CollisionSystem:
    """Handles all collision detection and physics"""
    def __init__(self, environment):
        self.environment = environment
        self.collision_penalties = {
            'bridge_strike': 5000,
            'off_road_fine': 100,
            'general_collision': 250
        }
    
    def check_truck_collisions(self, truck, player_data):
        """Check all possible truck collisions"""
        truck_rect = truck.get_rect()
        results = {
            'bridge_strike': False,
            'off_road': False,
            'fuel_station': None,
            'speed_multiplier': 1.0,
            'penalties': []
        }
        
        # Bridge collision check
        bridge_hit = self.environment.check_bridge_collisions(truck_rect, truck_height=15)
        if bridge_hit:
            results['bridge_strike'] = True
            results['penalties'].append(('Bridge Strike!', self.collision_penalties['bridge_strike']))
        
        # Off-road check
        if not self.environment.is_on_road(truck.x, truck.y):
            results['off_road'] = True
            results['speed_multiplier'] = self.environment.off_road_penalty
        else:
            results['speed_multiplier'] = self.environment.get_speed_multiplier(truck.x, truck.y)
        
        # Fuel station check
        results['fuel_station'] = self.environment.get_nearby_fuel_station(truck_rect)
        
        return results
