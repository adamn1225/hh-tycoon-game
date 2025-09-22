"""
Heavy Haul Tycoon - Integrated Game Flow
Contract Selection → Driving Mission → Results Screen
"""
import pygame
import sys
import math
import json
import random

# Load game data
def load_cities():
    try:
        with open('data/cities.json', 'r') as f:
            return json.load(f)['cities']
    except FileNotFoundError:
        return [
            {"name": "Tampa", "x": 100, "y": 420},
            {"name": "Atlanta", "x": 240, "y": 280},
            {"name": "Dallas", "x": 120, "y": 360},
            {"name": "Phoenix", "x": 60, "y": 380}
        ]

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Heavy Haul Tycoon - Integrated")
clock = pygame.time.Clock()

# Fonts
SMALL_FONT = pygame.font.SysFont(None, 18)
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
BASE_RATE_PER_MILE = 6.00
FUEL_DRAIN_RATE = 0.008  # Reduced from 0.03 to make fuel last longer
BRIDGE_PENALTY = 5000

class GameState:
    def __init__(self):
        self.cash = 10000
        self.fuel = 100.0
        self.current_contract = None
        self.scene = "contracts"  # contracts, driving, results
        self.mission_start_time = 0
        self.mission_penalties = []
        self.mission_completed = False

class Contract:
    def __init__(self, origin_city, dest_city, cargo_type, deadline_hours):
        self.origin = origin_city
        self.destination = dest_city
        self.cargo_type = cargo_type
        self.deadline_hours = deadline_hours
        
        # Calculate distance and payment
        dx = abs(dest_city['x'] - origin_city['x'])
        dy = abs(dest_city['y'] - origin_city['y'])
        self.distance_miles = (dx + dy) / 10
        
        # Payment calculation
        weight_multipliers = {'Standard': 1.1, 'Oversize': 1.25, 'Superload': 1.5}
        oversize_bonuses = {'Standard': 0.0, 'Oversize': 0.20, 'Superload': 0.40}
        
        base_payment = BASE_RATE_PER_MILE * self.distance_miles
        weight_factor = weight_multipliers[cargo_type] - 1
        oversize_factor = oversize_bonuses[cargo_type]
        
        if deadline_hours <= 4:
            deadline_multiplier = 1.3
        elif deadline_hours <= 6:
            deadline_multiplier = 1.15
        else:
            deadline_multiplier = 1.0
            
        self.payout = int(base_payment * (1 + weight_factor + oversize_factor) * deadline_multiplier)
        
        # Cargo description
        descriptions = {
            'Standard': ['Steel Coils', 'Lumber', 'Electronics'],
            'Oversize': ['Construction Equipment', 'Industrial Machinery'],
            'Superload': ['Wind Turbine Blades', 'Bridge Sections']
        }
        self.cargo_description = random.choice(descriptions[cargo_type])

class Truck:
    def __init__(self, start_x, start_y):
        self.x = start_x
        self.y = start_y
        self.angle = 0
        self.speed = 0
        self.max_speed = 4.0
        self.acceleration = 0.15
        self.deceleration = 0.1
        self.turn_speed = 2.5
        
    def update(self, keys, dt, speed_multiplier=1.0):
        """Update truck position and rotation based on input"""
        # Acceleration/Deceleration
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.speed = min(self.speed + self.acceleration, self.max_speed * speed_multiplier)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.speed = max(self.speed - self.acceleration, -self.max_speed * 0.5)
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
        return pygame.Rect(self.x - 30, self.y - 15, 60, 30)
    
    def draw(self, screen):
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

def generate_contracts(cities, num=3):
    """Generate contracts using city data"""
    contracts = []
    cargo_types = ['Standard', 'Oversize', 'Superload']
    
    for _ in range(num):
        origin = random.choice(cities)
        destinations = [c for c in cities if c['name'] != origin['name']]
        destination = random.choice(destinations)
        
        cargo_type = random.choices(cargo_types, weights=[0.5, 0.3, 0.2])[0]
        
        # Calculate deadline based on distance
        distance = ((abs(destination['x'] - origin['x']) + abs(destination['y'] - origin['y'])) / 10)
        base_time = max(3, int(distance / 15))  # More generous time
        deadline = base_time + random.randint(2, 6)  # More generous buffer
        deadline = max(5, min(15, deadline))  # At least 5 hours, up to 15
        
        contract = Contract(origin, destination, cargo_type, deadline)
        contracts.append(contract)
    
    return contracts

def render_contract_screen(game_state, cities):
    """Contract selection screen"""
    screen.fill(BLACK)
    
    # Title
    title_text = TITLE_FONT.render("Select Rate Confirmation", True, WHITE)
    title_rect = title_text.get_rect(center=(400, 50))
    screen.blit(title_text, title_rect)
    
    # Cash
    cash_text = LARGE_FONT.render(f"Cash: ${game_state.cash:,}", True, GREEN)
    screen.blit(cash_text, (50, 100))
    
    # Generate contracts if none exist
    if not hasattr(game_state, 'available_contracts'):
        game_state.available_contracts = generate_contracts(cities)
    
    # Draw contract cards (simplified)
    card_y = 150
    for i, contract in enumerate(game_state.available_contracts):
        card_x = 50 + i * 250
        card_rect = pygame.Rect(card_x, card_y, 230, 160)
        
        # Card background
        pygame.draw.rect(screen, DARK_GRAY, card_rect, border_radius=8)
        pygame.draw.rect(screen, WHITE, card_rect, 2, border_radius=8)
        
        # Contract info
        y_offset = card_y + 10
        
        # Route
        route_text = f"{contract.origin['name']} → {contract.destination['name']}"
        route_surface = FONT.render(route_text, True, WHITE)
        screen.blit(route_surface, (card_x + 10, y_offset))
        y_offset += 25
        
        # Cargo
        cargo_surface = SMALL_FONT.render(f"{contract.cargo_description}", True, LIGHT_GRAY)
        screen.blit(cargo_surface, (card_x + 10, y_offset))
        y_offset += 18
        
        # Type
        type_colors = {'Standard': WHITE, 'Oversize': YELLOW, 'Superload': ORANGE}
        type_surface = SMALL_FONT.render(f"Type: {contract.cargo_type}", True, type_colors[contract.cargo_type])
        screen.blit(type_surface, (card_x + 10, y_offset))
        y_offset += 18
        
        # Distance
        distance_surface = SMALL_FONT.render(f"Distance: {contract.distance_miles:.1f} mi", True, LIGHT_GRAY)
        screen.blit(distance_surface, (card_x + 10, y_offset))
        y_offset += 18
        
        # Deadline
        deadline_surface = SMALL_FONT.render(f"Deadline: {contract.deadline_hours}h", True, YELLOW)
        screen.blit(deadline_surface, (card_x + 10, y_offset))
        y_offset += 18
        
        # Payment
        payment_surface = FONT.render(f"${contract.payout:,}", True, GREEN)
        screen.blit(payment_surface, (card_x + 10, y_offset))
        
        # Number to select
        number_text = LARGE_FONT.render(str(i + 1), True, WHITE)
        screen.blit(number_text, (card_x + 200, card_y + 10))
    
    # Instructions
    instruction_text = FONT.render("Press 1, 2, or 3 to select Rate Con", True, WHITE)
    screen.blit(instruction_text, (250, 350))

def render_driving_screen(game_state, truck, elapsed_time):
    """Driving mission screen"""
    screen.fill(GRASS_GREEN)
    
    # Enhanced road network with turns
    # Main horizontal road
    main_road = pygame.Rect(0, 250, 800, 100)
    pygame.draw.rect(screen, ROAD_GRAY, main_road)
    
    # Vertical connecting roads
    north_road = pygame.Rect(150, 100, 100, 200)
    pygame.draw.rect(screen, ROAD_GRAY, north_road)
    
    south_road = pygame.Rect(550, 300, 100, 200)
    pygame.draw.rect(screen, ROAD_GRAY, south_road)
    
    # Road markings - main road
    for x in range(0, 800, 40):
        pygame.draw.rect(screen, YELLOW, (x, 295, 20, 5))
    
    # Road markings - vertical roads
    for y in range(100, 300, 40):
        pygame.draw.rect(screen, YELLOW, (195, y, 5, 20))
    for y in range(300, 500, 40):
        pygame.draw.rect(screen, YELLOW, (595, y, 5, 20))
    
    # Road borders
    pygame.draw.rect(screen, WHITE, main_road, 2)
    pygame.draw.rect(screen, WHITE, north_road, 2)
    pygame.draw.rect(screen, WHITE, south_road, 2)
    
    # Fuel stations
    fuel_station1 = pygame.Rect(100, 180, 80, 60)
    fuel_station2 = pygame.Rect(620, 400, 80, 60)
    
    # Draw fuel stations
    pygame.draw.rect(screen, LIGHT_GRAY, fuel_station1)
    pygame.draw.rect(screen, DARK_GRAY, fuel_station1, 2)
    pygame.draw.rect(screen, LIGHT_GRAY, fuel_station2)
    pygame.draw.rect(screen, DARK_GRAY, fuel_station2, 2)
    
    # Fuel pumps
    pump1a = pygame.Rect(110, 240, 15, 20)
    pump1b = pygame.Rect(155, 240, 15, 20)
    pump2a = pygame.Rect(630, 460, 15, 20)
    pump2b = pygame.Rect(675, 460, 15, 20)
    pygame.draw.rect(screen, RED, pump1a)
    pygame.draw.rect(screen, RED, pump1b)
    pygame.draw.rect(screen, RED, pump2a)
    pygame.draw.rect(screen, RED, pump2b)
    
    # Fuel station signs
    fuel_price_text = "$4.50/gal"
    price1 = SMALL_FONT.render(fuel_price_text, True, WHITE)
    price2 = SMALL_FONT.render(fuel_price_text, True, WHITE)
    screen.blit(price1, (fuel_station1.x, fuel_station1.y - 20))
    screen.blit(price2, (fuel_station2.x, fuel_station2.y - 20))
    
    # Bridge hazard
    bridge = pygame.Rect(400, 230, 80, 40)
    pygame.draw.rect(screen, GRAY, bridge)
    pygame.draw.rect(screen, DARK_GRAY, bridge, 3)
    
    # Bridge warning sign
    warning_rect = pygame.Rect(350, 200, 100, 25)
    pygame.draw.rect(screen, YELLOW, warning_rect)
    pygame.draw.rect(screen, BLACK, warning_rect, 2)
    clearance_text = SMALL_FONT.render("CLEARANCE 12'", True, BLACK)
    text_rect = clearance_text.get_rect(center=warning_rect.center)
    screen.blit(clearance_text, text_rect)
    
    # Destination zone (based on contract destination city position)
    dest_x = game_state.current_contract.destination['x'] * 6  # Scale for bigger map
    dest_y = game_state.current_contract.destination['y'] * 1.2
    dest_radius = 50
    
    # Pulsing destination
    pulse = abs(math.sin(elapsed_time * 3))
    inner_radius = int(dest_radius * 0.7 + pulse * 10)
    pygame.draw.circle(screen, GREEN, (int(dest_x), int(dest_y)), dest_radius, 3)
    pygame.draw.circle(screen, (0, 255, 0), (int(dest_x), int(dest_y)), inner_radius)
    
    # Destination label
    dest_text = FONT.render(game_state.current_contract.destination['name'], True, WHITE)
    text_rect = dest_text.get_rect(center=(dest_x, dest_y - dest_radius - 20))
    pygame.draw.rect(screen, BLACK, text_rect.inflate(10, 5), border_radius=3)
    screen.blit(dest_text, text_rect)
    
    # Draw truck
    truck.draw(screen)
    
    # Check for fuel station interaction
    station1_zone = fuel_station1.inflate(40, 40)
    station2_zone = fuel_station2.inflate(40, 40)
    truck_rect = truck.get_rect()
    
    near_fuel_station = False
    if station1_zone.colliderect(truck_rect) or station2_zone.colliderect(truck_rect):
        near_fuel_station = True
        if game_state.fuel < 100:
            # Show refuel prompt
            refuel_text = FONT.render("Press R to refuel ($50)", True, YELLOW)
            screen.blit(refuel_text, (truck.x - 60, truck.y - 40))
            
            # Check for refuel input in the main game loop
            if not hasattr(game_state, 'refuel_available'):
                game_state.refuel_available = True
        else:
            full_text = FONT.render("Tank Full", True, GREEN)
            screen.blit(full_text, (truck.x - 30, truck.y - 40))
    else:
        game_state.refuel_available = False
    
    # Check bridge collision
    bridge_danger = pygame.Rect(400, 250, 80, 20)
    if bridge_danger.colliderect(truck_rect):
        # Bridge strike penalty (but don't end mission immediately)
        if not hasattr(game_state, 'bridge_penalty_applied'):
            game_state.mission_penalties.append(5000)
            game_state.bridge_penalty_applied = True
        # Show warning but don't end mission
        warning_text = FONT.render("BRIDGE STRIKE! $5000 PENALTY", True, RED)
        screen.blit(warning_text, (truck.x - 100, truck.y - 60))
    
    # Check if truck is on road
    roads = [main_road, north_road, south_road]
    on_road = any(road.collidepoint(truck.x, truck.y) for road in roads)
    if not on_road and abs(truck.speed) > 0:
        # Off-road warning
        if not hasattr(game_state, 'off_road_warning_time'):
            game_state.off_road_warning_time = 0
        game_state.off_road_warning_time += 1/60  # Assuming 60 FPS
        if game_state.off_road_warning_time > 120:  # 2 seconds
            offroad_text = FONT.render("OFF-ROAD: Stay on the road!", True, ORANGE)
            screen.blit(offroad_text, (truck.x - 80, truck.y - 60))
    else:
        game_state.off_road_warning_time = 0
    
    # HUD
    render_hud(game_state, truck, elapsed_time, dest_x, dest_y, on_road)
    
    # Check delivery
    distance_to_dest = math.sqrt((truck.x - dest_x) ** 2 + (truck.y - dest_y) ** 2)
    if distance_to_dest < dest_radius and not game_state.mission_completed:
        print(f"DEBUG: Mission completed! Distance to dest: {distance_to_dest}")
        game_state.mission_completed = True
        return "delivery_complete"  # Mission complete
    
    return "continue"

def render_hud(game_state, truck, elapsed_time, dest_x, dest_y, on_road=True):
    """Render HUD elements"""
    # Fuel gauge
    fuel_bg = pygame.Rect(20, 20, 200, 25)
    fuel_percent = game_state.fuel / 100
    fuel_width = fuel_percent * 196
    fuel_bar = pygame.Rect(22, 22, fuel_width, 21)
    
    pygame.draw.rect(screen, DARK_GRAY, fuel_bg, border_radius=4)
    if fuel_percent > 0.5:
        fuel_color = GREEN
    elif fuel_percent > 0.25:
        fuel_color = YELLOW
    else:
        fuel_color = RED
    
    pygame.draw.rect(screen, fuel_color, fuel_bar, border_radius=3)
    pygame.draw.rect(screen, WHITE, fuel_bg, 2, border_radius=4)
    
    fuel_text = FONT.render(f"Fuel: {game_state.fuel:.1f}%", True, WHITE)
    screen.blit(fuel_text, (230, 22))
    
    # Speed indicator with off-road warning
    speed_color = WHITE if on_road else ORANGE
    speed_text = FONT.render(f"Speed: {abs(truck.speed):.1f} mph", True, speed_color)
    screen.blit(speed_text, (20, 55))
    
    if not on_road:
        offroad_indicator = FONT.render("OFF-ROAD", True, ORANGE)
        screen.blit(offroad_indicator, (150, 55))
    
    # Cash
    cash_text = FONT.render(f"Cash: ${game_state.cash:,}", True, GREEN)
    screen.blit(cash_text, (20, 85))
    
    # Mission timer
    time_remaining = max(0, game_state.current_contract.deadline_hours * 3600 - elapsed_time)
    minutes = int(time_remaining // 60)
    seconds = int(time_remaining % 60)
    timer_color = RED if time_remaining < 120 else WHITE
    timer_text = FONT.render(f"Time: {minutes:02d}:{seconds:02d}", True, timer_color)
    screen.blit(timer_text, (20, 115))
    
    # Distance to destination
    distance = math.sqrt((truck.x - dest_x) ** 2 + (truck.y - dest_y) ** 2)
    dist_text = FONT.render(f"Distance: {distance/10:.1f} mi", True, WHITE)
    screen.blit(dist_text, (20, 145))
    
    # Contract info
    contract_text = FONT.render(f"Delivering: {game_state.current_contract.cargo_description}", True, WHITE)
    screen.blit(contract_text, (20, 175))

def render_results_screen(game_state, mission_time, time_bonus, penalties):
    """Mission results screen"""
    screen.fill(BLACK)
    
    # Title
    if game_state.mission_completed:
        title_text = TITLE_FONT.render("DELIVERY COMPLETE!", True, GREEN)
    else:
        title_text = TITLE_FONT.render("MISSION FAILED", True, RED)
    
    title_rect = title_text.get_rect(center=(400, 100))
    screen.blit(title_text, title_rect)
    
    # Results breakdown
    y_offset = 200
    
    # Predicted vs actual
    predicted_text = FONT.render(f"Predicted Payment: ${game_state.current_contract.payout:,}", True, WHITE)
    screen.blit(predicted_text, (100, y_offset))
    y_offset += 30
    
    if game_state.mission_completed:
        actual_payment = game_state.current_contract.payout + time_bonus - sum(penalties)
        actual_text = FONT.render(f"Actual Payment: ${actual_payment:,}", True, GREEN)
        screen.blit(actual_text, (100, y_offset))
        y_offset += 30
        
        if time_bonus > 0:
            bonus_text = FONT.render(f"Time Bonus: +${time_bonus:,}", True, GREEN)
            screen.blit(bonus_text, (120, y_offset))
            y_offset += 25
        
        if penalties:
            penalty_text = FONT.render(f"Penalties: -${sum(penalties):,}", True, RED)
            screen.blit(penalty_text, (120, y_offset))
            y_offset += 25
    else:
        actual_text = FONT.render("Payment: $0", True, RED)
        screen.blit(actual_text, (100, y_offset))
        y_offset += 30
    
    # Mission time
    minutes = int(mission_time // 60)
    seconds = int(mission_time % 60)
    time_text = FONT.render(f"Mission Time: {minutes:02d}:{seconds:02d}", True, WHITE)
    screen.blit(time_text, (100, y_offset))
    y_offset += 30
    
    # Final cash
    final_cash_text = LARGE_FONT.render(f"Total Cash: ${game_state.cash:,}", True, GREEN)
    screen.blit(final_cash_text, (100, y_offset + 20))
    
    # Continue instruction
    continue_text = FONT.render("Press SPACE for new contract | ESC to quit", True, WHITE)
    screen.blit(continue_text, (200, 500))

def main():
    """Main game loop"""
    game_state = GameState()
    cities = load_cities()
    truck = None
    mission_start_time = 0
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif game_state.scene == "contracts":
                    # Contract selection
                    if event.key == pygame.K_1 and len(game_state.available_contracts) > 0:
                        game_state.current_contract = game_state.available_contracts[0]
                        print(f"DEBUG: Starting contract with {game_state.current_contract.deadline_hours}h deadline")
                        game_state.scene = "driving"
                        # Start truck at safe position away from bridge
                        truck = Truck(100, 300)  # Safe starting position on main road
                        mission_start_time = pygame.time.get_ticks() / 1000.0
                        print(f"DEBUG: Mission start time: {mission_start_time}")
                        game_state.mission_start_time = mission_start_time
                        game_state.mission_completed = False
                        game_state.mission_penalties = []
                        game_state.bridge_penalty_applied = False  # Reset bridge penalty flag
                    elif event.key == pygame.K_2 and len(game_state.available_contracts) > 1:
                        game_state.current_contract = game_state.available_contracts[1]
                        game_state.scene = "driving"
                        truck = Truck(100, 300)  # Safe starting position on main road
                        mission_start_time = pygame.time.get_ticks() / 1000.0
                        game_state.mission_start_time = mission_start_time
                        game_state.mission_completed = False
                        game_state.mission_penalties = []
                        game_state.bridge_penalty_applied = False
                    elif event.key == pygame.K_3 and len(game_state.available_contracts) > 2:
                        game_state.current_contract = game_state.available_contracts[2]
                        game_state.scene = "driving"
                        truck = Truck(100, 300)  # Safe starting position on main road
                        mission_start_time = pygame.time.get_ticks() / 1000.0
                        game_state.mission_start_time = mission_start_time
                        game_state.mission_completed = False
                        game_state.mission_penalties = []
                        game_state.bridge_penalty_applied = False
                elif game_state.scene == "results":
                    if event.key == pygame.K_SPACE:
                        # New contract
                        game_state.scene = "contracts"
                        game_state.available_contracts = generate_contracts(cities)
                        print(f"DEBUG: Generated {len(game_state.available_contracts)} new contracts")
                        game_state.fuel = 100.0  # Refuel between missions
        
        # Game logic based on scene
        if game_state.scene == "contracts":
            render_contract_screen(game_state, cities)
            
        elif game_state.scene == "driving":
            keys = pygame.key.get_pressed()
            
            # Handle refueling
            if hasattr(game_state, 'refuel_available') and game_state.refuel_available:
                if keys[pygame.K_r] and game_state.cash >= 50 and game_state.fuel < 100:
                    game_state.fuel = 100.0
                    game_state.cash -= 50
            
            # Update truck
            if game_state.fuel > 0:
                truck.update(keys, dt)
                
                # Fuel consumption
                if abs(truck.speed) > 0.1:
                    fuel_before = game_state.fuel
                    game_state.fuel -= FUEL_DRAIN_RATE * (1 + abs(truck.speed) / 5)
                    game_state.fuel = max(0, game_state.fuel)
                    if elapsed_time < 5:  # Debug for first 5 seconds
                        print(f"DEBUG: Fuel drain - Before: {fuel_before:.2f}, After: {game_state.fuel:.2f}, Speed: {truck.speed:.2f}")
            else:
                print(f"DEBUG: No fuel! Game should end. Fuel: {game_state.fuel}")
                # If out of fuel, mission fails immediately
                game_state.scene = "results"
            
            # Mission timer
            elapsed_time = pygame.time.get_ticks() / 1000.0 - game_state.mission_start_time
            
            # Debug logging
            if elapsed_time < 5:  # Only log for first 5 seconds
                print(f"DEBUG: Elapsed time: {elapsed_time:.2f}s, Fuel: {game_state.fuel:.1f}, Deadline: {game_state.current_contract.deadline_hours}h ({game_state.current_contract.deadline_hours * 3600}s)")
            
            # Check mission completion
            mission_complete = render_driving_screen(game_state, truck, elapsed_time)
            
            # More debug logging
            if mission_complete:
                print(f"DEBUG: Mission complete returned: {mission_complete}")
            
            deadline_seconds = game_state.current_contract.deadline_hours * 3600
            if elapsed_time > deadline_seconds:
                print(f"DEBUG: Time exceeded! {elapsed_time:.2f}s > {deadline_seconds}s")
            
            # Fix: Check for specific completion states, not just any truthy value
            mission_ended = (mission_complete == "delivery_complete") or elapsed_time > deadline_seconds
            
            if mission_ended:
                # Calculate results
                print(f"DEBUG: Mission ending - Complete: {mission_complete}, Time over: {elapsed_time > deadline_seconds}")
                print(f"DEBUG: Mission completed flag: {game_state.mission_completed}")
                mission_time = elapsed_time
                time_remaining = max(0, game_state.current_contract.deadline_hours * 3600 - elapsed_time)
                time_bonus = int(time_remaining * 10) if game_state.mission_completed else 0
                penalties = sum(game_state.mission_penalties)
                
                if game_state.mission_completed:
                    actual_payment = game_state.current_contract.payout + time_bonus - penalties
                    game_state.cash += actual_payment
                    print(f"DEBUG: Mission SUCCESS - Payment: {actual_payment}")
                else:
                    print(f"DEBUG: Mission FAILED - No payment")
                
                game_state.scene = "results"
                game_state.last_mission_time = mission_time
                game_state.last_time_bonus = time_bonus
                game_state.last_penalties = game_state.mission_penalties
            
        elif game_state.scene == "results":
            render_results_screen(game_state, game_state.last_mission_time, 
                                game_state.last_time_bonus, game_state.last_penalties)
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
