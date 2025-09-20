"""
Heavy Haul Tycoon - Upgrade System
Uses config.yml parameters for truck improvements
"""
import pygame
import sys
import yaml

# Load upgrade configuration
def load_config():
    try:
        with open('data/config.yml', 'r') as f:
            return yaml.safe_load(f)
    except (FileNotFoundError, ImportError):
        # Fallback config if YAML not available
        return {
            'upgrades': {
                'engine': {
                    'levels': [1, 2, 3],
                    'costs': [5000, 12000, 25000],
                    'speed_bonuses': [1.0, 1.3, 1.6]
                },
                'fuel_tank': {
                    'levels': [1, 2, 3],
                    'costs': [3000, 8000, 15000],
                    'capacities': [100, 200, 300]
                },
                'frame': {
                    'levels': [1, 2, 3],
                    'costs': [4000, 10000, 20000],
                    'collision_reduction': [1.0, 0.75, 0.5]
                }
            }
        }

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Heavy Haul Tycoon - Upgrades")
clock = pygame.time.Clock()

# Fonts
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
GRAY = (128, 128, 128)
DARK_GRAY = (60, 60, 60)
LIGHT_GRAY = (200, 200, 200)

class TruckUpgrades:
    def __init__(self, config):
        self.config = config['upgrades']
        self.engine_level = 1
        self.fuel_tank_level = 1
        self.frame_level = 1
        
    def get_engine_stats(self):
        """Get current engine upgrade stats"""
        level_index = self.engine_level - 1
        return {
            'level': self.engine_level,
            'speed_multiplier': self.config['engine']['speed_bonuses'][level_index],
            'next_cost': self.config['engine']['costs'][level_index + 1] if level_index + 1 < len(self.config['engine']['costs']) else None,
            'max_level': len(self.config['engine']['levels'])
        }
    
    def get_fuel_tank_stats(self):
        """Get current fuel tank upgrade stats"""
        level_index = self.fuel_tank_level - 1
        return {
            'level': self.fuel_tank_level,
            'capacity': self.config['fuel_tank']['capacities'][level_index],
            'next_cost': self.config['fuel_tank']['costs'][level_index + 1] if level_index + 1 < len(self.config['fuel_tank']['costs']) else None,
            'max_level': len(self.config['fuel_tank']['levels'])
        }
    
    def get_frame_stats(self):
        """Get current frame upgrade stats"""
        level_index = self.frame_level - 1
        return {
            'level': self.frame_level,
            'damage_reduction': 1.0 - self.config['frame']['collision_reduction'][level_index],
            'next_cost': self.config['frame']['costs'][level_index + 1] if level_index + 1 < len(self.config['frame']['costs']) else None,
            'max_level': len(self.config['frame']['levels'])
        }
    
    def can_upgrade_engine(self, cash):
        """Check if engine can be upgraded"""
        stats = self.get_engine_stats()
        return stats['next_cost'] is not None and cash >= stats['next_cost']
    
    def can_upgrade_fuel_tank(self, cash):
        """Check if fuel tank can be upgraded"""
        stats = self.get_fuel_tank_stats()
        return stats['next_cost'] is not None and cash >= stats['next_cost']
    
    def can_upgrade_frame(self, cash):
        """Check if frame can be upgraded"""
        stats = self.get_frame_stats()
        return stats['next_cost'] is not None and cash >= stats['next_cost']
    
    def upgrade_engine(self, cash):
        """Upgrade engine if possible"""
        stats = self.get_engine_stats()
        if self.can_upgrade_engine(cash):
            self.engine_level += 1
            return stats['next_cost']
        return 0
    
    def upgrade_fuel_tank(self, cash):
        """Upgrade fuel tank if possible"""
        stats = self.get_fuel_tank_stats()
        if self.can_upgrade_fuel_tank(cash):
            self.fuel_tank_level += 1
            return stats['next_cost']
        return 0
    
    def upgrade_frame(self, cash):
        """Upgrade frame if possible"""
        stats = self.get_frame_stats()
        if self.can_upgrade_frame(cash):
            self.frame_level += 1
            return stats['next_cost']
        return 0

class UpgradeCard:
    def __init__(self, x, y, upgrade_type, truck_upgrades, width=240, height=200):
        self.rect = pygame.Rect(x, y, width, height)
        self.upgrade_type = upgrade_type
        self.truck_upgrades = truck_upgrades
        self.button_rect = pygame.Rect(x + 10, y + height - 35, width - 20, 25)
        self.hovered = False
        
    def handle_event(self, event, cash):
        """Handle upgrade button clicks"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_rect.collidepoint(event.pos):
                if self.upgrade_type == "engine":
                    return self.truck_upgrades.upgrade_engine(cash)
                elif self.upgrade_type == "fuel_tank":
                    return self.truck_upgrades.upgrade_fuel_tank(cash)
                elif self.upgrade_type == "frame":
                    return self.truck_upgrades.upgrade_frame(cash)
        return 0
    
    def update(self, mouse_pos):
        """Update hover state"""
        self.hovered = self.button_rect.collidepoint(mouse_pos)
    
    def render(self, screen, cash):
        """Render upgrade card"""
        # Get stats based on upgrade type
        if self.upgrade_type == "engine":
            stats = self.truck_upgrades.get_engine_stats()
            title = "Engine Upgrade"
            current_desc = f"Speed: {stats['speed_multiplier']:.1f}x"
            next_desc = f"Next: {stats['speed_multiplier'] * 1.3:.1f}x speed" if stats['next_cost'] else "MAX LEVEL"
        elif self.upgrade_type == "fuel_tank":
            stats = self.truck_upgrades.get_fuel_tank_stats()
            title = "Fuel Tank Upgrade"
            current_desc = f"Capacity: {stats['capacity']} gallons"
            next_desc = f"Next: {stats['capacity'] + 100} gallons" if stats['next_cost'] else "MAX LEVEL"
        elif self.upgrade_type == "frame":
            stats = self.truck_upgrades.get_frame_stats()
            title = "Frame Upgrade"
            current_desc = f"Damage Reduction: {stats['damage_reduction']*100:.0f}%"
            next_desc = f"Next: {(1.0 - stats['damage_reduction']) * 0.75 * 100:.0f}% reduction" if stats['next_cost'] else "MAX LEVEL"
        
        # Card background
        card_color = DARK_GRAY if not self.hovered else (80, 80, 80)
        pygame.draw.rect(screen, card_color, self.rect, border_radius=8)
        pygame.draw.rect(screen, LIGHT_GRAY, self.rect, 2, border_radius=8)
        
        # Card content
        y_offset = self.rect.y + 15
        x_margin = self.rect.x + 15
        
        # Title
        title_surface = LARGE_FONT.render(title, True, WHITE)
        screen.blit(title_surface, (x_margin, y_offset))
        y_offset += 35
        
        # Current level
        level_text = f"Level: {stats['level']}/{stats['max_level']}"
        level_surface = FONT.render(level_text, True, YELLOW)
        screen.blit(level_surface, (x_margin, y_offset))
        y_offset += 25
        
        # Current stats
        current_surface = FONT.render(current_desc, True, GREEN)
        screen.blit(current_surface, (x_margin, y_offset))
        y_offset += 25
        
        # Next upgrade description
        next_color = LIGHT_GRAY if stats['next_cost'] else GRAY
        next_surface = FONT.render(next_desc, True, next_color)
        screen.blit(next_surface, (x_margin, y_offset))
        y_offset += 25
        
        # Cost
        if stats['next_cost']:
            cost_text = f"Cost: ${stats['next_cost']:,}"
            cost_color = GREEN if cash >= stats['next_cost'] else RED
            cost_surface = FONT.render(cost_text, True, cost_color)
            screen.blit(cost_surface, (x_margin, y_offset))
        
        # Upgrade button
        if stats['next_cost']:
            can_afford = cash >= stats['next_cost']
            button_color = (0, 150, 0) if self.hovered and can_afford else (0, 120, 0) if can_afford else (100, 100, 100)
            pygame.draw.rect(screen, button_color, self.button_rect, border_radius=4)
            pygame.draw.rect(screen, WHITE, self.button_rect, 2, border_radius=4)
            
            button_text = "UPGRADE" if can_afford else "NOT ENOUGH CASH"
            text_color = WHITE if can_afford else GRAY
            button_surface = FONT.render(button_text, True, text_color)
            text_rect = button_surface.get_rect(center=self.button_rect.center)
            screen.blit(button_surface, text_rect)
        else:
            # Max level button
            pygame.draw.rect(screen, GRAY, self.button_rect, border_radius=4)
            pygame.draw.rect(screen, WHITE, self.button_rect, 2, border_radius=4)
            
            max_surface = FONT.render("MAX LEVEL", True, WHITE)
            text_rect = max_surface.get_rect(center=self.button_rect.center)
            screen.blit(max_surface, text_rect)

def main_upgrade_screen():
    """Upgrade shop screen"""
    config = load_config()
    truck_upgrades = TruckUpgrades(config)
    cash = 50000  # Start with more cash for testing
    
    # Create upgrade cards
    upgrade_cards = [
        UpgradeCard(50, 150, "engine", truck_upgrades),
        UpgradeCard(310, 150, "fuel_tank", truck_upgrades),
        UpgradeCard(570, 150, "frame", truck_upgrades)
    ]
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            # Handle upgrade purchases
            for card in upgrade_cards:
                cost = card.handle_event(event, cash)
                if cost > 0:
                    cash -= cost
                    print(f"Upgraded {card.upgrade_type} for ${cost:,}! Cash remaining: ${cash:,}")
        
        # Update card hover states
        for card in upgrade_cards:
            card.update(mouse_pos)
        
        # Rendering
        screen.fill(BLACK)
        
        # Title
        title_text = TITLE_FONT.render("Truck Upgrades", True, WHITE)
        title_rect = title_text.get_rect(center=(400, 50))
        screen.blit(title_text, title_rect)
        
        # Cash display
        cash_text = LARGE_FONT.render(f"Cash: ${cash:,}", True, GREEN)
        screen.blit(cash_text, (50, 100))
        
        # Upgrade cards
        for card in upgrade_cards:
            card.render(screen, cash)
        
        # Instructions
        instruction_text = FONT.render("Click on upgrade cards to improve your truck | ESC to quit", True, WHITE)
        screen.blit(instruction_text, (150, 380))
        
        # Current truck stats summary
        engine_stats = truck_upgrades.get_engine_stats()
        tank_stats = truck_upgrades.get_fuel_tank_stats()
        frame_stats = truck_upgrades.get_frame_stats()
        
        summary_y = 450
        summary_texts = [
            f"Current Truck: Engine Lv{engine_stats['level']} | Tank Lv{tank_stats['level']} | Frame Lv{frame_stats['level']}",
            f"Performance: {engine_stats['speed_multiplier']:.1f}x Speed | {tank_stats['capacity']} Fuel | {frame_stats['damage_reduction']*100:.0f}% Damage Protection"
        ]
        
        for i, text in enumerate(summary_texts):
            summary_surface = FONT.render(text, True, LIGHT_GRAY)
            screen.blit(summary_surface, (50, summary_y + i * 25))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_upgrade_screen()
