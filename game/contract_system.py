"""
Heavy Haul Tycoon - Contract System Implementation
Uses cities.json data to generate dynamic delivery contracts
"""
import pygame
import sys
import math
import json
import random
import os

# Load cities data
def load_cities():
    try:
        with open('data/cities.json', 'r') as f:
            return json.load(f)['cities']
    except FileNotFoundError:
        # Fallback cities if file not found
        return [
            {"name": "Tampa", "x": 100, "y": 420},
            {"name": "Atlanta", "x": 240, "y": 280},
            {"name": "Dallas", "x": 120, "y": 360},
            {"name": "Phoenix", "x": 60, "y": 380}
        ]

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Heavy Haul Tycoon - Contract System")
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

# Game balance from your plan
BASE_RATE_PER_MILE = 6.00
WEIGHT_MULTIPLIERS = {
    'Standard': 1.1,
    'Oversize': 1.25,
    'Superload': 1.5
}
OVERSIZE_BONUSES = {
    'Standard': 0.0,
    'Oversize': 0.20,
    'Superload': 0.40
}

class Contract:
    def __init__(self, origin_city, dest_city, cargo_type, deadline_hours):
        self.origin = origin_city
        self.destination = dest_city
        self.cargo_type = cargo_type
        self.deadline_hours = deadline_hours
        
        # Calculate distance using your plan's formula: (|dx| + |dy|) / 10
        dx = abs(dest_city['x'] - origin_city['x'])
        dy = abs(dest_city['y'] - origin_city['y'])
        self.distance_miles = (dx + dy) / 10
        
        # Calculate payment using your revenue formula
        self.base_payment = BASE_RATE_PER_MILE * self.distance_miles
        self.weight_factor = WEIGHT_MULTIPLIERS[cargo_type] - 1  # Convert to bonus
        self.oversize_factor = OVERSIZE_BONUSES[cargo_type]
        
        # Deadline multiplier (tighter deadlines = more money)
        if deadline_hours <= 4:
            self.deadline_multiplier = 1.3  # Urgent
        elif deadline_hours <= 6:
            self.deadline_multiplier = 1.15  # Standard
        else:
            self.deadline_multiplier = 1.0  # Relaxed
        
        # Final payout calculation
        self.payout = int(self.base_payment * (1 + self.weight_factor + self.oversize_factor) * self.deadline_multiplier)
        
        # Generate cargo description
        self.cargo_descriptions = {
            'Standard': ['Steel Coils', 'Lumber', 'Electronics', 'Food Products', 'Textiles'],
            'Oversize': ['Construction Equipment', 'Industrial Machinery', 'Prefab Buildings', 'Large Tanks'],
            'Superload': ['Wind Turbine Blades', 'Bridge Sections', 'Transformers', 'Mining Equipment']
        }
        self.cargo_description = random.choice(self.cargo_descriptions[cargo_type])

class ContractCard:
    def __init__(self, contract, x, y, card_width=240, card_height=180):
        self.contract = contract
        self.rect = pygame.Rect(x, y, card_width, card_height)
        self.button_rect = pygame.Rect(x + 10, y + card_height - 35, card_width - 20, 25)
        self.hovered = False
        self.clicked = False
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_rect.collidepoint(event.pos):
                self.clicked = True
                return True
        return False
    
    def update(self, mouse_pos):
        self.hovered = self.button_rect.collidepoint(mouse_pos)
    
    def render(self, screen):
        # Card background
        card_color = DARK_GRAY if not self.hovered else (80, 80, 80)
        pygame.draw.rect(screen, card_color, self.rect, border_radius=8)
        pygame.draw.rect(screen, LIGHT_GRAY, self.rect, 2, border_radius=8)
        
        # Card content
        y_offset = self.rect.y + 10
        x_margin = self.rect.x + 10
        
        # Route header
        route_text = f"{self.contract.origin['name']} → {self.contract.destination['name']}"
        route_surface = FONT.render(route_text, True, WHITE)
        screen.blit(route_surface, (x_margin, y_offset))
        y_offset += 25
        
        # Cargo info
        cargo_text = f"Cargo: {self.contract.cargo_description}"
        cargo_surface = SMALL_FONT.render(cargo_text, True, LIGHT_GRAY)
        screen.blit(cargo_surface, (x_margin, y_offset))
        y_offset += 18
        
        # Cargo type with color coding
        type_colors = {'Standard': WHITE, 'Oversize': YELLOW, 'Superload': ORANGE}
        type_text = f"Type: {self.contract.cargo_type}"
        type_surface = SMALL_FONT.render(type_text, True, type_colors[self.contract.cargo_type])
        screen.blit(type_surface, (x_margin, y_offset))
        y_offset += 18
        
        # Distance
        distance_text = f"Distance: {self.contract.distance_miles:.1f} miles"
        distance_surface = SMALL_FONT.render(distance_text, True, LIGHT_GRAY)
        screen.blit(distance_surface, (x_margin, y_offset))
        y_offset += 18
        
        # Deadline
        deadline_color = RED if self.contract.deadline_hours <= 4 else YELLOW if self.contract.deadline_hours <= 6 else GREEN
        deadline_text = f"Deadline: {self.contract.deadline_hours} hours"
        deadline_surface = SMALL_FONT.render(deadline_text, True, deadline_color)
        screen.blit(deadline_surface, (x_margin, y_offset))
        y_offset += 18
        
        # Payment (highlighted)
        payment_text = f"Payment: ${self.contract.payout:,}"
        payment_surface = FONT.render(payment_text, True, GREEN)
        screen.blit(payment_surface, (x_margin, y_offset))
        
        # Accept button
        button_color = (0, 150, 0) if self.hovered else (0, 120, 0)
        pygame.draw.rect(screen, button_color, self.button_rect, border_radius=4)
        pygame.draw.rect(screen, WHITE, self.button_rect, 2, border_radius=4)
        
        button_text = FONT.render("Accept Contract", True, WHITE)
        text_rect = button_text.get_rect(center=self.button_rect.center)
        screen.blit(button_text, text_rect)

class ContractGenerator:
    def __init__(self, cities):
        self.cities = cities
        self.cargo_types = ['Standard', 'Oversize', 'Superload']
        
    def generate_contracts(self, num_contracts=3):
        """Generate random contracts based on cities data"""
        contracts = []
        
        for _ in range(num_contracts):
            # Pick random origin and destination (different cities)
            origin = random.choice(self.cities)
            available_destinations = [city for city in self.cities if city['name'] != origin['name']]
            destination = random.choice(available_destinations)
            
            # Random cargo type (weighted toward standard)
            cargo_weights = [0.5, 0.3, 0.2]  # Standard, Oversize, Superload
            cargo_type = random.choices(self.cargo_types, weights=cargo_weights)[0]
            
            # Random deadline based on distance and cargo type
            base_time = max(2, int(((abs(destination['x'] - origin['x']) + abs(destination['y'] - origin['y'])) / 10) / 20))
            if cargo_type == 'Superload':
                deadline = base_time + random.randint(2, 4)
            elif cargo_type == 'Oversize':
                deadline = base_time + random.randint(1, 3)
            else:
                deadline = base_time + random.randint(0, 2)
            
            deadline = max(3, min(12, deadline))  # Keep between 3-12 hours
            
            contract = Contract(origin, destination, cargo_type, deadline)
            contracts.append(contract)
        
        return contracts

def main_contract_screen():
    """Contract selection screen"""
    cities = load_cities()
    generator = ContractGenerator(cities)
    cash = 10000
    
    # Generate initial contracts
    contracts = generator.generate_contracts(3)
    contract_cards = [
        ContractCard(contracts[0], 50, 150),
        ContractCard(contracts[1], 310, 150),
        ContractCard(contracts[2], 570, 150)
    ]
    
    selected_contract = None
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    # Refresh contracts
                    contracts = generator.generate_contracts(3)
                    contract_cards = [
                        ContractCard(contracts[0], 50, 150),
                        ContractCard(contracts[1], 310, 150),
                        ContractCard(contracts[2], 570, 150)
                    ]
            
            # Check contract selections
            for i, card in enumerate(contract_cards):
                if card.handle_event(event):
                    selected_contract = contracts[i]
                    print(f"\nSelected Contract:")
                    print(f"Route: {selected_contract.origin['name']} → {selected_contract.destination['name']}")
                    print(f"Cargo: {selected_contract.cargo_description} ({selected_contract.cargo_type})")
                    print(f"Distance: {selected_contract.distance_miles:.1f} miles")
                    print(f"Deadline: {selected_contract.deadline_hours} hours")
                    print(f"Payment: ${selected_contract.payout:,}")
                    print(f"Payment Breakdown:")
                    print(f"  Base: ${selected_contract.base_payment:.0f}")
                    print(f"  Weight Bonus: +{selected_contract.weight_factor*100:.0f}%")
                    print(f"  Oversize Bonus: +{selected_contract.oversize_factor*100:.0f}%")
                    print(f"  Deadline Multiplier: {selected_contract.deadline_multiplier:.2f}x")
        
        # Update card hover states
        for card in contract_cards:
            card.update(mouse_pos)
        
        # Rendering
        screen.fill(BLACK)
        
        # Title
        title_text = TITLE_FONT.render("Available Contracts", True, WHITE)
        title_rect = title_text.get_rect(center=(400, 50))
        screen.blit(title_text, title_rect)
        
        # Cash display
        cash_text = LARGE_FONT.render(f"Cash: ${cash:,}", True, GREEN)
        screen.blit(cash_text, (50, 100))
        
        # Instructions
        instruction_text = FONT.render("Press R to refresh contracts | ESC to quit", True, LIGHT_GRAY)
        screen.blit(instruction_text, (50, 380))
        
        # Contract cards
        for card in contract_cards:
            card.render(screen)
        
        # Selection feedback
        if selected_contract:
            feedback_y = 420
            feedback_text = FONT.render(f"Contract selected! Ready to start delivery mission.", True, GREEN)
            screen.blit(feedback_text, (50, feedback_y))
            
            details_text = SMALL_FONT.render(f"Route: {selected_contract.origin['name']} → {selected_contract.destination['name']} | Payment: ${selected_contract.payout:,}", True, WHITE)
            screen.blit(details_text, (50, feedback_y + 25))
        
        # Contract generation info (debug)
        info_y = 500
        info_texts = [
            f"Cities loaded: {len(cities)}",
            f"Revenue formula: Base Rate (${BASE_RATE_PER_MILE}/mi) × Distance × Weight × Oversize × Deadline",
            "Contract types: Standard (50%), Oversize (30%), Superload (20%)"
        ]
        
        for i, text in enumerate(info_texts):
            info_surface = SMALL_FONT.render(text, True, GRAY)
            screen.blit(info_surface, (50, info_y + i * 15))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_contract_screen()
