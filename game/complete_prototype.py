"""
Heavy Haul Tycoon - Complete Standalone Prototype
All systems integrated in one file for easy testing
"""
import pygame
import sys
import math

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Heavy Haul Tycoon - Prototype v0.1")
clock = pygame.time.Clock()

# Fonts
SMALL_FONT = pygame.font.SysFont(None, 20)
FONT = pygame.font.SysFont(None, 24)
LARGE_FONT = pygame.font.SysFont(None, 32)
TITLE_FONT = pygame.font.SysFont(None, 48)

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

# Game constants
TRUCK_MAX_SPEED = 4.0
FUEL_DRAIN_RATE = 0.03
FUEL_PRICE = 4.50
BRIDGE_PENALTY = 5000

class Truck:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.max_speed = TRUCK_MAX_SPEED
        self.acceleration = 0.15
        self.deceleration = 0.1
        self.turn_speed = 2.5
        
    def update(self, keys, dt, speed_multiplier=1.0):
        # Acceleration/Deceleration
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.speed = min(self.speed + self.acceleration, self.max_speed * speed_multiplier)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.speed = max(self.speed - self.acceleration, -self.max_speed * 0.5 * speed_multiplier)
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
        
        # Keep on screen
        self.x = max(30, min(770, self.x))
        self.y = max(30, min(570, self.y))
    
    def get_rect(self):
        return pygame.Rect(self.x - 30, self.y - 15, 60, 30)
    
    def draw(self, screen):
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
        
        # Wheels
        wheel_positions = [
            (self.x + 10 * cos_a - 8 * sin_a, self.y + 10 * sin_a + 8 * cos_a),
            (self.x + 10 * cos_a + 8 * sin_a, self.y + 10 * sin_a - 8 * cos_a),
            (self.x - 15 * cos_a - 8 * sin_a, self.y - 15 * sin_a + 8 * cos_a),
            (self.x - 15 * cos_a + 8 * sin_a, self.y - 15 * sin_a - 8 * cos_a),
        ]
        
        for wheel_x, wheel_y in wheel_positions:
            pygame.draw.circle(screen, BLACK, (int(wheel_x), int(wheel_y)), 3)
    
    def _get_rotated_rect(self, center_x, center_y, width, height, angle):
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

class Environment:
    def __init__(self):
        # Roads
        self.main_road = pygame.Rect(0, 250, 800, 100)
        self.side_road1 = pygame.Rect(150, 150, 100, 200)
        self.side_road2 = pygame.Rect(550, 150, 100, 200)
        
        # Bridge
        self.bridge = pygame.Rect(400, 230, 80, 40)
        self.bridge_danger_zone = pygame.Rect(400, 250, 80, 20)
        
        # Fuel stations
        self.fuel_station1 = pygame.Rect(100, 180, 80, 60)
        self.fuel_station2 = pygame.Rect(650, 180, 80, 60)
        
    def is_on_road(self, x, y):
        return (self.main_road.collidepoint(x, y) or 
                self.side_road1.collidepoint(x, y) or 
                self.side_road2.collidepoint(x, y))
    
    def check_bridge_collision(self, truck_rect):
        return self.bridge_danger_zone.colliderect(truck_rect)
    
    def get_fuel_station_nearby(self, truck_rect):
        station1_zone = self.fuel_station1.inflate(40, 40)
        station2_zone = self.fuel_station2.inflate(40, 40)
        
        if station1_zone.colliderect(truck_rect):
            return self.fuel_station1
        elif station2_zone.colliderect(truck_rect):
            return self.fuel_station2
        return None
    
    def render(self, screen):
        # Background
        screen.fill(GRASS_GREEN)
        
        # Roads
        pygame.draw.rect(screen, ROAD_GRAY, self.main_road)
        pygame.draw.rect(screen, ROAD_GRAY, self.side_road1)
        pygame.draw.rect(screen, ROAD_GRAY, self.side_road2)
        
        # Road markings
        for x in range(0, 800, 40):
            pygame.draw.rect(screen, YELLOW, (x, 295, 20, 5))
        
        # Road edges
        pygame.draw.rect(screen, WHITE, self.main_road, 2)
        pygame.draw.rect(screen, WHITE, self.side_road1, 2)
        pygame.draw.rect(screen, WHITE, self.side_road2, 2)
        
        # Fuel stations
        pygame.draw.rect(screen, LIGHT_GRAY, self.fuel_station1)
        pygame.draw.rect(screen, DARK_GRAY, self.fuel_station1, 2)
        pygame.draw.rect(screen, LIGHT_GRAY, self.fuel_station2)
        pygame.draw.rect(screen, DARK_GRAY, self.fuel_station2, 2)
        
        # Fuel station signs
        fuel_text = SMALL_FONT.render(f"${FUEL_PRICE:.2f}/gal", True, WHITE)
        screen.blit(fuel_text, (self.fuel_station1.x, self.fuel_station1.y - 20))
        screen.blit(fuel_text, (self.fuel_station2.x, self.fuel_station2.y - 20))
        
        # Bridge
        pygame.draw.rect(screen, GRAY, self.bridge)
        pygame.draw.rect(screen, DARK_GRAY, self.bridge, 3)
        
        # Bridge warning
        warning_rect = pygame.Rect(self.bridge.x - 50, self.bridge.y - 30, 100, 25)
        pygame.draw.rect(screen, YELLOW, warning_rect)
        pygame.draw.rect(screen, BLACK, warning_rect, 2)
        clearance_text = SMALL_FONT.render("CLEARANCE 12'", True, BLACK)
        text_rect = clearance_text.get_rect(center=warning_rect.center)
        screen.blit(clearance_text, text_rect)

class DeliveryZone:
    def __init__(self, x, y, radius=40):
        self.x = x
        self.y = y
        self.radius = radius
        self.flash_timer = 0
        
    def check_delivery(self, truck_x, truck_y):
        distance = math.sqrt((truck_x - self.x) ** 2 + (truck_y - self.y) ** 2)
        return distance <= self.radius
    
    def update(self, dt):
        self.flash_timer += dt * 3
    
    def render(self, screen):
        pulse = abs(math.sin(self.flash_timer))
        inner_radius = int(self.radius * 0.7 + pulse * 10)
        
        pygame.draw.circle(screen, GREEN, (int(self.x), int(self.y)), self.radius, 3)
        pygame.draw.circle(screen, (0, 255, 0), (int(self.x), int(self.y)), inner_radius)
        
        dest_text = FONT.render("DELIVERY", True, WHITE)
        text_rect = dest_text.get_rect(center=(self.x, self.y - self.radius - 20))
        bg_rect = text_rect.inflate(10, 5)
        pygame.draw.rect(screen, BLACK, bg_rect, border_radius=3)
        screen.blit(dest_text, text_rect)

def render_fuel_gauge(fuel, x=20, y=20):
    gauge_bg = pygame.Rect(x, y, 200, 25)
    fuel_percentage = max(0, fuel / 100)
    fuel_width = fuel_percentage * 196
    fuel_bar = pygame.Rect(x + 2, y + 2, fuel_width, 21)
    
    pygame.draw.rect(screen, DARK_GRAY, gauge_bg, border_radius=4)
    
    if fuel_percentage > 0.5:
        fuel_color = GREEN
    elif fuel_percentage > 0.25:
        fuel_color = YELLOW
    else:
        fuel_color = RED
    
    pygame.draw.rect(screen, fuel_color, fuel_bar, border_radius=3)
    pygame.draw.rect(screen, WHITE, gauge_bg, 2, border_radius=4)
    
    fuel_text = FONT.render(f"Fuel: {fuel:.1f}%", True, WHITE)
    screen.blit(fuel_text, (x + 210, y + 2))

def render_hud(speed, cash, fuel, time_remaining=None, distance_to_target=0):
    # Fuel gauge
    render_fuel_gauge(fuel)
    
    # Speed
    speed_text = FONT.render(f"Speed: {abs(speed):.1f} mph", True, WHITE)
    screen.blit(speed_text, (20, 55))
    
    # Cash
    cash_text = FONT.render(f"Cash: ${cash:,}", True, GREEN)
    screen.blit(cash_text, (20, 85))
    
    # Timer
    if time_remaining is not None:
        minutes = int(time_remaining // 60)
        seconds = int(time_remaining % 60)
        color = RED if time_remaining < 120 else WHITE
        timer_text = FONT.render(f"Time: {minutes:02d}:{seconds:02d}", True, color)
        screen.blit(timer_text, (20, 115))
    
    # Distance to target
    if distance_to_target > 10:
        dist_text = FONT.render(f"Distance: {distance_to_target/10:.1f} mi", True, WHITE)
        screen.blit(dist_text, (20, 145))

def main_game():
    # Game state
    truck = Truck(150, 300)
    environment = Environment()
    delivery_zone = DeliveryZone(650, 300)
    
    # Mission state
    fuel = 100.0
    cash = 10000
    mission_time = 8 * 60  # 8 minutes for demo
    elapsed_time = 0
    mission_active = True
    mission_completed = False
    
    # Message system
    messages = []
    
    def add_message(text, color=WHITE, duration=3.0):
        messages.append({'text': text, 'color': color, 'time': duration})
    
    add_message("Deliver cargo to the green zone!", GREEN)
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    # Refuel
                    station = environment.get_fuel_station_nearby(truck.get_rect())
                    if station and fuel < 100:
                        fuel_needed = 100 - fuel
                        cost = fuel_needed * FUEL_PRICE
                        if cash >= cost:
                            cash -= int(cost)
                            fuel = 100.0
                            add_message(f"Refueled! Cost: ${cost:.0f}", YELLOW)
                        else:
                            add_message("Not enough cash!", RED)
        
        if not mission_active:
            continue
        
        # Input
        keys = pygame.key.get_pressed()
        
        # Check environment
        on_road = environment.is_on_road(truck.x, truck.y)
        speed_multiplier = 1.0 if on_road else 0.5
        
        # Bridge collision
        if environment.check_bridge_collision(truck.get_rect()):
            mission_active = False
            cash -= BRIDGE_PENALTY
            add_message("MISSION FAILED! Bridge Strike!", RED, 5.0)
            add_message(f"Penalty: ${BRIDGE_PENALTY:,}", RED, 5.0)
            continue
        
        # Update truck
        if fuel > 0:
            truck.update(keys, dt, speed_multiplier)
            
            # Fuel consumption
            if abs(truck.speed) > 0.1:
                consumption = FUEL_DRAIN_RATE * (1 + abs(truck.speed) / 5)
                if not on_road:
                    consumption *= 1.5
                fuel -= consumption
                fuel = max(0, fuel)
        else:
            truck.speed = 0
            add_message("OUT OF FUEL! Find a fuel station!", RED, 5.0)
        
        # Off-road warning
        if not on_road and abs(truck.speed) > 0:
            if not hasattr(main_game, 'off_road_timer'):
                main_game.off_road_timer = 0
            main_game.off_road_timer += dt
            if main_game.off_road_timer > 2:
                add_message("OFF-ROAD: Reduced speed!", ORANGE)
                main_game.off_road_timer = 0
        
        # Fuel station prompt
        if environment.get_fuel_station_nearby(truck.get_rect()):
            if not hasattr(main_game, 'refuel_shown'):
                add_message("Press R to refuel", YELLOW)
                main_game.refuel_shown = True
        else:
            if hasattr(main_game, 'refuel_shown'):
                delattr(main_game, 'refuel_shown')
        
        # Update delivery zone
        delivery_zone.update(dt)
        
        # Check delivery
        if delivery_zone.check_delivery(truck.x, truck.y) and not mission_completed:
            mission_completed = True
            mission_active = False
            
            # Calculate payment
            time_remaining = max(0, mission_time - elapsed_time)
            base_payment = 2500
            time_bonus = int(time_remaining * 10)
            total_payment = base_payment + time_bonus
            
            cash += total_payment
            add_message("DELIVERY COMPLETE!", GREEN, 5.0)
            add_message(f"Payment: ${total_payment:,}", GREEN, 5.0)
        
        # Update timer
        elapsed_time += dt
        time_remaining = max(0, mission_time - elapsed_time)
        
        if time_remaining <= 0 and not mission_completed:
            mission_active = False
            add_message("TIME'S UP! Mission failed!", RED, 5.0)
        
        # Update messages
        for msg in messages[:]:
            msg['time'] -= dt
            if msg['time'] <= 0:
                messages.remove(msg)
        
        # Calculate distance to target
        distance = math.sqrt((truck.x - delivery_zone.x) ** 2 + (truck.y - delivery_zone.y) ** 2)
        
        # Render
        environment.render(screen)
        delivery_zone.render(screen)
        truck.draw(screen)
        
        # HUD
        render_hud(truck.speed, cash, fuel, time_remaining, distance)
        
        # Messages
        y_offset = 200
        for msg in messages:
            msg_text = FONT.render(msg['text'], True, msg['color'])
            bg_rect = msg_text.get_rect()
            bg_rect.x = 20
            bg_rect.y = y_offset
            bg_rect.inflate_ip(10, 5)
            
            bg_surface = pygame.Surface(bg_rect.size)
            bg_surface.fill(BLACK)
            bg_surface.set_alpha(128)
            screen.blit(bg_surface, bg_rect)
            screen.blit(msg_text, (25, y_offset + 2))
            y_offset += 30
        
        # Mission status overlay
        if mission_completed:
            overlay = pygame.Surface((800, 600))
            overlay.fill(BLACK)
            overlay.set_alpha(128)
            screen.blit(overlay, (0, 0))
            
            victory_text = TITLE_FONT.render("DELIVERY COMPLETE!", True, GREEN)
            text_rect = victory_text.get_rect(center=(400, 250))
            screen.blit(victory_text, text_rect)
            
            continue_text = FONT.render("Press ESC to exit", True, WHITE)
            text_rect = continue_text.get_rect(center=(400, 350))
            screen.blit(continue_text, text_rect)
        
        # Instructions
        if elapsed_time < 10:  # Show for first 10 seconds
            instructions = [
                "Arrow Keys/WASD: Drive",
                "R: Refuel at stations",
                "Avoid the bridge!",
                "Stay on roads for better speed"
            ]
            
            for i, instruction in enumerate(instructions):
                text = SMALL_FONT.render(instruction, True, WHITE)
                screen.blit(text, (550, 450 + i * 20))
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_game()
