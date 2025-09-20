"""
Heavy Haul Tycoon - Main Game
Complete prototype with all core systems integrated
"""
import pygame
import sys
import math
import os

# Add the game directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from core.engine import GameEngine, Scene, GameState, Config
    from core.ui import HUD, Button
    from systems.driving import Environment, DeliveryZone, CollisionSystem
except ImportError as e:
    print(f"Import error: {e}")
    print("Running simplified standalone version...")
    # We'll define everything inline for now

# Import the enhanced truck class from our previous work
class Truck:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0  # Facing right initially
        self.speed = 0
        self.max_speed = Config.TRUCK_MAX_SPEED
        self.acceleration = Config.TRUCK_ACCELERATION
        self.deceleration = Config.TRUCK_DECELERATION
        self.turn_speed = Config.TRUCK_TURN_SPEED
        
        # Truck components
        self.cab_width = 35
        self.cab_height = 20
        self.trailer_width = 50
        self.trailer_height = 15
        
        # Physics state
        self.speed_multiplier = 1.0
        
    def update(self, keys, dt, speed_multiplier=1.0):
        """Update truck position and rotation based on input"""
        self.speed_multiplier = speed_multiplier
        
        # Acceleration/Deceleration
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.speed = min(self.speed + self.acceleration, self.max_speed * speed_multiplier)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.speed = max(self.speed - self.acceleration, -self.max_speed * 0.5 * speed_multiplier)
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
    
    def draw(self, screen, colors):
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
        pygame.draw.polygon(screen, colors['light_gray'], trailer_points)
        pygame.draw.polygon(screen, colors['dark_gray'], trailer_points, 2)
        
        # Draw cab
        cab_points = self._get_rotated_rect(
            self.x, self.y, self.cab_width, self.cab_height, self.angle
        )
        pygame.draw.polygon(screen, colors['blue'], cab_points)
        pygame.draw.polygon(screen, colors['dark_gray'], cab_points, 2)
        
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
            pygame.draw.circle(screen, colors['black'], (int(wheel_x), int(wheel_y)), 3)
    
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

class DrivingScene(Scene):
    """Main driving gameplay scene"""
    
    def __init__(self, engine):
        super().__init__(engine)
        self.truck = Truck(150, 300)
        self.environment = Environment(800, 600)
        self.collision_system = CollisionSystem(self.environment)
        self.hud = HUD(engine)
        
        # Mission state
        self.delivery_zone = DeliveryZone(650, 300, 40)
        self.mission_active = True
        self.mission_completed = False
        
        # Game state
        self.fuel_consumption_rate = Config.FUEL_DRAIN_RATE
        self.penalties_this_mission = []
        
        # Initialize mission
        self.hud.set_destination(self.delivery_zone.x, self.delivery_zone.y)
        self.hud.start_mission(8)  # 8 hour deadline
        self.hud.add_status_message("Deliver cargo to the green zone!", (0, 255, 0))
    
    def handle_event(self, event):
        """Handle driving scene events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                # Refuel at station
                nearby_station = self.environment.get_nearby_fuel_station(self.truck.get_rect())
                if nearby_station and self.engine.player_data['fuel'] < 100:
                    self.refuel_at_station(nearby_station)
            elif event.key == pygame.K_SPACE:
                # Emergency brake / handbrake
                self.truck.speed *= 0.5
    
    def refuel_at_station(self, station):
        """Refuel at a fuel station"""
        fuel_needed = 100 - self.engine.player_data['fuel']
        cost = fuel_needed * station.fuel_price
        
        if self.engine.player_data['cash'] >= cost:
            self.engine.player_data['cash'] -= int(cost)
            self.engine.player_data['fuel'] = 100.0
            self.hud.add_status_message(f"Refueled! Cost: ${cost:.0f}", (255, 255, 0))
        else:
            self.hud.add_status_message("Not enough cash to refuel!", (255, 100, 100))
    
    def update(self, dt, keys):
        """Update driving scene"""
        if not self.mission_active:
            return
        
        # Check collisions first
        collision_results = self.collision_system.check_truck_collisions(self.truck, self.engine.player_data)
        
        # Handle bridge strikes (mission failure)
        if collision_results['bridge_strike']:
            self.mission_active = False
            self.hud.add_status_message("MISSION FAILED! Bridge Strike!", (255, 0, 0), 5.0)
            for penalty_text, penalty_amount in collision_results['penalties']:
                self.engine.player_data['cash'] -= penalty_amount
                self.penalties_this_mission.append((penalty_text, penalty_amount))
            return
        
        # Update truck with speed multiplier for off-road
        if self.engine.player_data['fuel'] > 0:
            self.truck.update(keys, dt, collision_results['speed_multiplier'])
            
            # Fuel consumption (more when moving, extra when off-road)
            if abs(self.truck.speed) > 0.1:
                consumption = self.fuel_consumption_rate * (1 + abs(self.truck.speed) / 5)
                if collision_results['off_road']:
                    consumption *= 1.5  # Extra fuel consumption off-road
                    
                self.engine.player_data['fuel'] -= consumption
                self.engine.player_data['fuel'] = max(0, self.engine.player_data['fuel'])
        else:
            # Out of fuel
            self.truck.speed = 0
            if not hasattr(self, 'tow_warning_shown'):
                self.hud.add_status_message("OUT OF FUEL! Press ESC to call towing service", (255, 0, 0), 10.0)
                self.tow_warning_shown = True
        
        # Show off-road warning
        if collision_results['off_road'] and abs(self.truck.speed) > 0:
            if not hasattr(self, 'off_road_warning_time'):
                self.off_road_warning_time = 0
            self.off_road_warning_time += dt
            if self.off_road_warning_time > 2.0:  # Show warning every 2 seconds
                self.hud.add_status_message("OFF-ROAD: Reduced speed and increased fuel consumption", (255, 165, 0))
                self.off_road_warning_time = 0
        else:
            self.off_road_warning_time = 0
        
        # Show refuel prompt
        if collision_results['fuel_station']:
            if not hasattr(self, 'refuel_prompt_shown'):
                self.hud.add_status_message("Press R to refuel", (255, 255, 0))
                self.refuel_prompt_shown = True
        else:
            self.refuel_prompt_shown = False
        
        # Update delivery zone
        self.delivery_zone.update(dt)
        
        # Check for delivery completion
        if self.delivery_zone.check_delivery(self.truck.x, self.truck.y):
            if not self.mission_completed:
                self.mission_completed = True
                self.mission_active = False
                self.complete_mission()
        
        # Update HUD
        self.hud.update(dt, self.engine.player_data, self.truck)
    
    def complete_mission(self):
        """Complete the delivery mission"""
        # Calculate payment
        base_payment = 2500
        time_remaining = self.hud.timer.get_time_remaining()
        time_bonus = int(time_remaining * 10)  # $10 per second remaining
        
        total_payment = base_payment + time_bonus
        
        # Apply any penalties
        total_penalties = sum(penalty[1] for penalty in self.penalties_this_mission)
        final_payment = max(0, total_payment - total_penalties)
        
        self.engine.player_data['cash'] += final_payment
        
        # Show completion message
        self.hud.add_status_message(f"DELIVERY COMPLETE! Payment: ${final_payment:,}", (0, 255, 0), 5.0)
        if time_bonus > 0:
            self.hud.add_status_message(f"Time Bonus: ${time_bonus:,}", (255, 255, 0), 5.0)
        
        # Add instructions for continuing
        self.hud.add_status_message("Press ESC to return to menu", (255, 255, 255), 10.0)
    
    def render(self):
        """Render the driving scene"""
        # Render environment
        self.environment.render(self.screen, self.engine.colors, self.engine.get_font('medium'))
        
        # Render delivery zone
        self.delivery_zone.render(self.screen, self.engine.colors, self.engine.get_font('medium'))
        
        # Render truck
        self.truck.draw(self.screen, self.engine.colors)
        
        # Render HUD
        self.hud.render(self.screen)
        
        # Mission status
        if self.mission_completed:
            # Victory overlay
            overlay = pygame.Surface((800, 600))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(128)
            self.screen.blit(overlay, (0, 0))
            
            victory_text = self.engine.get_font('title').render("DELIVERY COMPLETE!", True, (0, 255, 0))
            text_rect = victory_text.get_rect(center=(400, 250))
            self.screen.blit(victory_text, text_rect)
        
        elif not self.mission_active and hasattr(self, 'tow_warning_shown'):
            # Mission failed overlay
            overlay = pygame.Surface((800, 600))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(128)
            self.screen.blit(overlay, (0, 0))
            
            fail_text = self.engine.get_font('title').render("MISSION FAILED", True, (255, 0, 0))
            text_rect = fail_text.get_rect(center=(400, 250))
            self.screen.blit(fail_text, text_rect)

class MenuScene(Scene):
    """Main menu scene"""
    
    def __init__(self, engine):
        super().__init__(engine)
        self.title_font = engine.get_font('title')
        self.button_font = engine.get_font('large')
        
        # Create buttons
        self.start_button = Button(300, 300, 200, 50, "Start Delivery", self.button_font)
        self.quit_button = Button(300, 370, 200, 50, "Quit Game", self.button_font)
    
    def handle_event(self, event):
        """Handle menu events"""
        if self.start_button.handle_event(event):
            self.engine.set_scene('driving')
            
        if self.quit_button.handle_event(event):
            self.engine.running = False
    
    def update(self, dt, keys):
        """Update menu"""
        self.start_button.update(dt)
        self.quit_button.update(dt)
    
    def render(self):
        """Render menu"""
        self.screen.fill(self.engine.colors['black'])
        
        # Title
        title_text = self.title_font.render("Heavy Haul Tycoon", True, self.engine.colors['white'])
        title_rect = title_text.get_rect(center=(400, 150))
        self.screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text = self.engine.get_font('large').render("Prototype v0.1", True, self.engine.colors['gray'])
        subtitle_rect = subtitle_text.get_rect(center=(400, 200))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Player stats
        cash_text = self.engine.get_font('medium').render(f"Cash: ${self.engine.player_data['cash']:,}", True, self.engine.colors['green'])
        self.screen.blit(cash_text, (50, 50))
        
        fuel_text = self.engine.get_font('medium').render(f"Fuel: {self.engine.player_data['fuel']:.1f}%", True, self.engine.colors['white'])
        self.screen.blit(fuel_text, (50, 80))
        
        # Buttons
        self.start_button.render(self.screen)
        self.quit_button.render(self.screen)
        
        # Instructions
        instructions = [
            "Controls:",
            "Arrow Keys / WASD - Drive",
            "R - Refuel at station",
            "ESC - Menu / Pause"
        ]
        
        y_offset = 450
        for instruction in instructions:
            text = self.engine.get_font('medium').render(instruction, True, self.engine.colors['light_gray'])
            self.screen.blit(text, (50, y_offset))
            y_offset += 25

def main():
    """Main game function"""
    # Create game engine
    engine = GameEngine()
    
    # Create and add scenes
    menu_scene = MenuScene(engine)
    driving_scene = DrivingScene(engine)
    
    engine.add_scene('menu', menu_scene)
    engine.add_scene('driving', driving_scene)
    
    # Start with menu
    engine.set_scene('menu')
    
    # Run the game
    engine.run()

if __name__ == "__main__":
    main()
