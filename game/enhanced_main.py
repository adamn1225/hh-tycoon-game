import pygame
import math
import sys

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Heavy Haul Tycoon")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont(None, 24)
LARGE_FONT = pygame.font.SysFont(None, 32)

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

# Game constants
TRUCK_WIDTH = 60
TRUCK_HEIGHT = 25
TRAILER_WIDTH = 80
TRAILER_HEIGHT = 20

class Truck:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0  # Facing right initially
        self.speed = 0
        self.max_speed = 4.0
        self.acceleration = 0.15
        self.deceleration = 0.1
        self.turn_speed = 2.5
        
        # Truck components
        self.cab_width = 35
        self.cab_height = 20
        self.trailer_width = 50
        self.trailer_height = 15
        
    def update(self, keys, dt):
        """Update truck position and rotation based on input"""
        # Acceleration/Deceleration
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.speed = min(self.speed + self.acceleration, self.max_speed)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.speed = max(self.speed - self.acceleration, -self.max_speed * 0.5)
        else:
            # Natural deceleration
            if self.speed > 0:
                self.speed = max(0, self.speed - self.deceleration)
            elif self.speed < 0:
                self.speed = min(0, self.speed + self.deceleration)
        
        # Turning (only when moving)
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
        """Get collision rectangle for the truck"""
        return pygame.Rect(self.x - 30, self.y - 15, 60, 30)
    
    def draw(self, screen):
        """Draw the truck with cab and trailer"""
        # Calculate positions for cab and trailer
        rad = math.radians(self.angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        
        # Trailer (behind cab)
        trailer_offset_x = -25 * cos_a
        trailer_offset_y = -25 * sin_a
        trailer_x = self.x + trailer_offset_x
        trailer_y = self.y + trailer_offset_y
        
        # Draw trailer
        trailer_points = self._get_rotated_rect(
            trailer_x, trailer_y, self.trailer_width, self.trailer_height, self.angle
        )
        pygame.draw.polygon(screen, LIGHT_GRAY, trailer_points)
        pygame.draw.polygon(screen, DARK_GRAY, trailer_points, 2)
        
        # Draw cab
        cab_points = self._get_rotated_rect(
            self.x, self.y, self.cab_width, self.cab_height, self.angle
        )
        pygame.draw.polygon(screen, BLUE, cab_points)
        pygame.draw.polygon(screen, DARK_GRAY, cab_points, 2)
        
        # Draw cab windows (front)
        front_offset_x = 12 * cos_a
        front_offset_y = 12 * sin_a
        front_x = self.x + front_offset_x
        front_y = self.y + front_offset_y
        
        window_points = self._get_rotated_rect(
            front_x, front_y, 8, 12, self.angle
        )
        pygame.draw.polygon(screen, (150, 200, 255), window_points)
        
        # Draw wheels (simple circles)
        wheel_positions = [
            (self.x + 10 * cos_a - 8 * sin_a, self.y + 10 * sin_a + 8 * cos_a),
            (self.x + 10 * cos_a + 8 * sin_a, self.y + 10 * sin_a - 8 * cos_a),
            (self.x - 15 * cos_a - 8 * sin_a, self.y - 15 * sin_a + 8 * cos_a),
            (self.x - 15 * cos_a + 8 * sin_a, self.y - 15 * sin_a - 8 * cos_a),
        ]
        
        for wheel_x, wheel_y in wheel_positions:
            pygame.draw.circle(screen, BLACK, (int(wheel_x), int(wheel_y)), 3)
    
    def _get_rotated_rect(self, center_x, center_y, width, height, angle):
        """Get points for a rotated rectangle"""
        rad = math.radians(angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        
        # Half dimensions
        hw, hh = width / 2, height / 2
        
        # Corner offsets (before rotation)
        corners = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
        
        # Rotate and translate corners
        points = []
        for cx, cy in corners:
            rx = cx * cos_a - cy * sin_a
            ry = cx * sin_a + cy * cos_a
            points.append((center_x + rx, center_y + ry))
        
        return points

def render_fuel_gauge(current_fuel, max_fuel=100):
    """Draw enhanced fuel gauge"""
    gauge_bg = pygame.Rect(20, 20, 200, 25)
    fuel_percentage = max(0, current_fuel / max_fuel)
    fuel_width = fuel_percentage * 196
    fuel_bar = pygame.Rect(22, 22, fuel_width, 21)
    
    # Background
    pygame.draw.rect(screen, DARK_GRAY, gauge_bg, border_radius=4)
    
    # Fuel bar (color changes based on fuel level)
    if fuel_percentage > 0.5:
        fuel_color = GREEN
    elif fuel_percentage > 0.25:
        fuel_color = YELLOW
    else:
        fuel_color = RED
    
    pygame.draw.rect(screen, fuel_color, fuel_bar, border_radius=3)
    pygame.draw.rect(screen, WHITE, gauge_bg, 2, border_radius=4)
    
    # Fuel text
    fuel_text = FONT.render(f"Fuel: {current_fuel:.1f}%", True, WHITE)
    screen.blit(fuel_text, (230, 22))

def render_hud(speed, cash, fuel):
    """Render heads-up display"""
    # Speed indicator
    speed_text = FONT.render(f"Speed: {abs(speed):.1f} mph", True, WHITE)
    screen.blit(speed_text, (20, 55))
    
    # Cash display
    cash_text = FONT.render(f"Cash: ${cash:,}", True, GREEN)
    screen.blit(cash_text, (20, 85))
    
    # Fuel gauge
    render_fuel_gauge(fuel)

def main_loop():
    """Enhanced main game loop"""
    truck = Truck(400, 300)
    fuel = 100.0
    cash = 10000
    fuel_drain_rate = 0.03  # Per frame when moving
    
    running = True
    
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Input processing
        keys = pygame.key.get_pressed()
        
        # Update truck
        if fuel > 0:
            old_speed = truck.speed
            truck.update(keys, dt)
            
            # Fuel consumption based on speed
            if abs(truck.speed) > 0.1:
                fuel -= fuel_drain_rate * (1 + abs(truck.speed) / 5)
        else:
            # Can't move without fuel
            truck.speed = 0
        
        # Rendering
        screen.fill((40, 60, 40))  # Dark green background
        
        # Draw simple road (placeholder)
        road_rect = pygame.Rect(0, 250, 800, 100)
        pygame.draw.rect(screen, DARK_GRAY, road_rect)
        
        # Road lines
        for x in range(0, 800, 40):
            pygame.draw.rect(screen, YELLOW, (x, 295, 20, 5))
        
        # Draw truck
        truck.draw(screen)
        
        # Draw HUD
        render_hud(truck.speed, cash, fuel)
        
        # Fuel depletion warning
        if fuel <= 0:
            warning_text = LARGE_FONT.render("OUT OF FUEL - Call Towing Service!", True, RED)
            text_rect = warning_text.get_rect(center=(400, 150))
            pygame.draw.rect(screen, BLACK, text_rect.inflate(20, 10), border_radius=5)
            screen.blit(warning_text, text_rect)
        
        # Instructions
        instructions = [
            "Arrow Keys / WASD: Drive",
            "ESC: Quit"
        ]
        for i, instruction in enumerate(instructions):
            text = FONT.render(instruction, True, WHITE)
            screen.blit(text, (20, 520 + i * 25))
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_loop()
