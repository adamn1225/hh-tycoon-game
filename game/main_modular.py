"""
Heavy Haul Tycoon - Modular Main Entry Point
Refactored for scalability and maintainability
"""
import pygame
import sys
from core.constants import *
from core.game_state import GameState
from data.loader import load_cities, generate_contracts
from entities.truck import Truck
from scenes.contracts import ContractScene
from systems.fuel import FuelSystem
from systems.physics import PhysicsSystem
from rendering.hud import HUD

class Game:
    """Main game class that manages the overall game loop and systems"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Heavy Haul Tycoon - Modular")
        self.clock = pygame.time.Clock()
        
        # Initialize systems
        self.fonts = init_fonts()
        self.game_state = GameState()
        self.cities = load_cities()
        
        # Game systems
        self.fuel_system = FuelSystem()
        self.physics_system = PhysicsSystem()
        self.hud = HUD(self.fonts)
        
        # Scenes
        self.contract_scene = ContractScene(self.fonts, self.cities)
        
        # Game objects
        self.truck = None
        
        # Generate initial contracts
        self.game_state.available_contracts = generate_contracts(self.cities)
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                
                # Scene-specific event handling
                if self.game_state.scene == "contracts":
                    truck = self.contract_scene.handle_event(event, self.game_state)
                    if truck:  # Contract was selected
                        self.truck = truck
                elif self.game_state.scene == "results":
                    if event.key == pygame.K_SPACE:
                        self._start_new_contracts()
        
        return True
    
    def update(self, dt):
        """Update game logic"""
        if self.game_state.scene == "contracts":
            self.contract_scene.update(dt, self.game_state)
            
        elif self.game_state.scene == "driving":
            self._update_driving(dt)
            
        elif self.game_state.scene == "results":
            pass  # Results scene is static
    
    def _update_driving(self, dt):
        """Update driving gameplay"""
        # Safety check - ensure truck exists
        if self.truck is None:
            return
            
        keys = pygame.key.get_pressed()
        
        # Handle refueling
        self.fuel_system.check_refuel_availability(self.game_state, self.truck)
        if keys[pygame.K_r]:
            self.fuel_system.attempt_refuel(self.game_state)
        
        # Update truck physics
        if self.game_state.fuel > 0:
            self.truck.update(keys, dt)
            self.fuel_system.update_fuel_consumption(self.game_state, self.truck)
        else:
            # Out of fuel - mission fails
            self.game_state.switch_scene("results")
            self._calculate_mission_results()
            return
        
        # Physics and collision updates
        self.physics_system.update_off_road_timer(self.game_state, self.truck, dt)
        self.physics_system.check_bridge_collision(self.game_state, self.truck)
        
        # Check mission completion
        elapsed_time = pygame.time.get_ticks() / 1000.0 - self.game_state.mission_start_time
        dest_x, dest_y = self._get_destination_position()
        
        mission_complete = self.physics_system.check_delivery_completion(
            self.game_state, self.truck, dest_x, dest_y
        )
        
        deadline_exceeded = elapsed_time > self.game_state.current_contract.get_deadline_seconds()
        
        if mission_complete or deadline_exceeded:
            self.game_state.switch_scene("results")
            self._calculate_mission_results(elapsed_time)
    
    def _get_destination_position(self):
        """Get destination position on screen"""
        dest_x = self.game_state.current_contract.destination['x'] * 6
        dest_y = self.game_state.current_contract.destination['y'] * 1.2
        return dest_x, dest_y
    
    def _calculate_mission_results(self, mission_time=0):
        """Calculate and store mission results"""
        time_remaining = max(0, self.game_state.current_contract.get_deadline_seconds() - mission_time)
        time_bonus = int(time_remaining * 10) if self.game_state.mission_completed else 0
        penalties = sum(self.game_state.mission_penalties)
        
        payment = self.game_state.complete_mission(mission_time, time_bonus, self.game_state.mission_penalties)
    
    def _start_new_contracts(self):
        """Generate new contracts and return to contract selection"""
        self.game_state.switch_scene("contracts")
        self.game_state.available_contracts = generate_contracts(self.cities)
        self.game_state.fuel = STARTING_FUEL  # Refuel between missions
    
    def render(self):
        """Render the current scene"""
        if self.game_state.scene == "contracts":
            self.contract_scene.render(self.screen, self.game_state)
            
        elif self.game_state.scene == "driving":
            self._render_driving()
            
        elif self.game_state.scene == "results":
            self._render_results()
    
    def _render_driving(self):
        """Render driving scene"""
        # Safety check - ensure truck exists
        if self.truck is None:
            return
            
        self.screen.fill(GRASS_GREEN)
        
        # Render world elements
        self.physics_system.render_roads(self.screen)
        self.fuel_system.render_fuel_stations(self.screen, self.fonts)
        self.physics_system.render_bridge(self.screen, self.fonts)
        
        # Render destination
        dest_x, dest_y = self._get_destination_position()
        self._render_destination(dest_x, dest_y)
        
        # Render truck
        self.truck.draw(self.screen)
        
        # Render interactive elements
        self.fuel_system.render_refuel_prompts(self.screen, self.fonts, self.game_state, self.truck)
        self.physics_system.render_collision_warnings(self.screen, self.fonts, self.game_state, self.truck)
        
        # Render HUD
        elapsed_time = pygame.time.get_ticks() / 1000.0 - self.game_state.mission_start_time
        on_road = self.physics_system.is_on_road(self.truck)
        self.hud.render_driving_hud(self.screen, self.game_state, self.truck, elapsed_time, dest_x, dest_y, on_road)
    
    def _render_destination(self, dest_x, dest_y):
        """Render pulsing destination marker"""
        import math
        elapsed_time = pygame.time.get_ticks() / 1000.0 - self.game_state.mission_start_time
        dest_radius = 50
        
        # Pulsing effect
        pulse = abs(math.sin(elapsed_time * 3))
        inner_radius = int(dest_radius * 0.7 + pulse * 10)
        pygame.draw.circle(self.screen, GREEN, (int(dest_x), int(dest_y)), dest_radius, 3)
        pygame.draw.circle(self.screen, (0, 255, 0), (int(dest_x), int(dest_y)), inner_radius)
        
        # Destination label
        dest_text = self.fonts['normal'].render(self.game_state.current_contract.destination['name'], True, WHITE)
        text_rect = dest_text.get_rect(center=(dest_x, dest_y - dest_radius - 20))
        pygame.draw.rect(self.screen, BLACK, text_rect.inflate(10, 5), border_radius=3)
        self.screen.blit(dest_text, text_rect)
    
    def _render_results(self):
        """Render mission results screen"""
        self.screen.fill(BLACK)
        
        # Title
        if self.game_state.mission_completed:
            title_text = self.fonts['title'].render("DELIVERY COMPLETE!", True, GREEN)
        else:
            title_text = self.fonts['title'].render("MISSION FAILED", True, RED)
        
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)
        
        # Results breakdown
        y_offset = 200
        
        # Predicted vs actual payment
        predicted_text = self.fonts['normal'].render(f"Predicted Payment: ${self.game_state.current_contract.payout:,}", True, WHITE)
        self.screen.blit(predicted_text, (100, y_offset))
        y_offset += 30
        
        if self.game_state.mission_completed:
            actual_payment = (self.game_state.current_contract.payout + 
                            self.game_state.last_time_bonus - 
                            sum(self.game_state.last_penalties))
            actual_text = self.fonts['normal'].render(f"Actual Payment: ${actual_payment:,}", True, GREEN)
            self.screen.blit(actual_text, (100, y_offset))
            y_offset += 30
            
            if self.game_state.last_time_bonus > 0:
                bonus_text = self.fonts['normal'].render(f"Time Bonus: +${self.game_state.last_time_bonus:,}", True, GREEN)
                self.screen.blit(bonus_text, (120, y_offset))
                y_offset += 25
            
            if self.game_state.last_penalties:
                penalty_text = self.fonts['normal'].render(f"Penalties: -${sum(self.game_state.last_penalties):,}", True, RED)
                self.screen.blit(penalty_text, (120, y_offset))
                y_offset += 25
        else:
            actual_text = self.fonts['normal'].render("Payment: $0", True, RED)
            self.screen.blit(actual_text, (100, y_offset))
            y_offset += 30
        
        # Mission time
        minutes = int(self.game_state.last_mission_time // 60)
        seconds = int(self.game_state.last_mission_time % 60)
        time_text = self.fonts['normal'].render(f"Mission Time: {minutes:02d}:{seconds:02d}", True, WHITE)
        self.screen.blit(time_text, (100, y_offset))
        y_offset += 30
        
        # Final cash
        final_cash_text = self.fonts['large'].render(f"Total Cash: ${self.game_state.cash:,}", True, GREEN)
        self.screen.blit(final_cash_text, (100, y_offset + 20))
        
        # Continue instruction
        continue_text = self.fonts['normal'].render("Press SPACE for new contract | ESC to quit", True, WHITE)
        self.screen.blit(continue_text, (200, 500))
    
    def run(self):
        """Main game loop"""
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            
            running = self.handle_events()
            if not running:
                break
            
            self.update(dt)
            self.render()
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

def main():
    """Entry point"""
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
