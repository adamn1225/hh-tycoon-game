"""
Contract Selection Scene
"""
import pygame
from scenes.base_scene import BaseScene
from core.constants import *
from data.loader import generate_contracts
from entities.truck import Truck

class ContractScene(BaseScene):
    """Contract selection screen"""
    
    def __init__(self, fonts, cities):
        super().__init__(fonts)
        self.cities = cities
    
    def handle_event(self, event, game_state):
        """Handle contract selection input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1 and len(game_state.available_contracts) > 0:
                return self._select_contract(game_state, 0)
            elif event.key == pygame.K_2 and len(game_state.available_contracts) > 1:
                return self._select_contract(game_state, 1)
            elif event.key == pygame.K_3 and len(game_state.available_contracts) > 2:
                return self._select_contract(game_state, 2)
        return None
    
    def _select_contract(self, game_state, index):
        """Select a contract and transition to driving"""
        game_state.current_contract = game_state.available_contracts[index]
        game_state.switch_scene("driving")
        game_state.reset_mission_state()
        game_state.mission_start_time = pygame.time.get_ticks() / 1000.0
        
        # Create truck at safe starting position
        return Truck(100, 300)
    
    def update(self, dt, game_state):
        """Update contract scene"""
        # Generate contracts if none exist
        if not game_state.available_contracts:
            game_state.available_contracts = generate_contracts(self.cities)
    
    def render(self, screen, game_state):
        """Render contract selection screen"""
        screen.fill(BLACK)
        
        # Title
        title_text = self.fonts['title'].render("Select Rate Confirmation", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(title_text, title_rect)
        
        # Cash
        cash_text = self.fonts['large'].render(f"Cash: ${game_state.cash:,}", True, GREEN)
        screen.blit(cash_text, (50, 100))
        
        # Draw contract cards
        self._render_contract_cards(screen, game_state)
        
        # Instructions
        instruction_text = self.fonts['normal'].render("Press 1, 2, or 3 to select Rate Con", True, WHITE)
        screen.blit(instruction_text, (250, 350))
    
    def _render_contract_cards(self, screen, game_state):
        """Render individual contract cards"""
        card_y = 150
        type_colors = {'Standard': WHITE, 'Oversize': YELLOW, 'Superload': ORANGE}
        
        for i, contract in enumerate(game_state.available_contracts):
            card_x = 50 + i * 250
            card_rect = pygame.Rect(card_x, card_y, 230, 160)
            
            # Card background
            pygame.draw.rect(screen, DARK_GRAY, card_rect, border_radius=8)
            pygame.draw.rect(screen, WHITE, card_rect, 2, border_radius=8)
            
            # Contract info
            y_offset = card_y + 10
            
            # Route
            route_surface = self.fonts['normal'].render(contract.route_text, True, WHITE)
            screen.blit(route_surface, (card_x + 10, y_offset))
            y_offset += 25
            
            # Cargo
            cargo_surface = self.fonts['small'].render(contract.cargo_description, True, LIGHT_GRAY)
            screen.blit(cargo_surface, (card_x + 10, y_offset))
            y_offset += 18
            
            # Type
            type_surface = self.fonts['small'].render(f"Type: {contract.cargo_type}", True, type_colors[contract.cargo_type])
            screen.blit(type_surface, (card_x + 10, y_offset))
            y_offset += 18
            
            # Distance
            distance_surface = self.fonts['small'].render(f"Distance: {contract.distance_miles:.1f} mi", True, LIGHT_GRAY)
            screen.blit(distance_surface, (card_x + 10, y_offset))
            y_offset += 18
            
            # Deadline
            deadline_surface = self.fonts['small'].render(f"Deadline: {contract.deadline_hours}h", True, YELLOW)
            screen.blit(deadline_surface, (card_x + 10, y_offset))
            y_offset += 18
            
            # Payment
            payment_surface = self.fonts['normal'].render(f"${contract.payout:,}", True, GREEN)
            screen.blit(payment_surface, (card_x + 10, y_offset))
            
            # Number to select
            number_text = self.fonts['large'].render(str(i + 1), True, WHITE)
            screen.blit(number_text, (card_x + 200, card_y + 10))
