import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
FONT = pygame.font.SysFont(None, 32)
SMALL_FONT = pygame.font.SysFont(None, 24)

class Button:
    def __init__(self, x, y, width, height, text, color=(100, 100, 100), text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.hovered = False
        self.clicked = False
    
    def handle_event(self, event):
        """Returns True if button was clicked"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.clicked = True
                return True
        return False
    
    def update(self, mouse_pos):
        """Update hover state"""
        self.hovered = self.rect.collidepoint(mouse_pos)
    
    def draw(self, screen):
        """Draw the button"""
        # Change color when hovered
        color = (150, 150, 150) if self.hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2, border_radius=5)  # Border
        
        # Center the text
        text_surface = FONT.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class ContractCard:
    def __init__(self, x, y, route, cargo, distance, payment, deadline):
        self.rect = pygame.Rect(x, y, 240, 150)
        self.route = route
        self.cargo = cargo
        self.distance = distance
        self.payment = payment
        self.deadline = deadline
        self.button = Button(x + 10, y + 120, 220, 25, "Accept Contract", (0, 120, 0))
    
    def handle_event(self, event):
        return self.button.handle_event(event)
    
    def update(self, mouse_pos):
        self.button.update(mouse_pos)
    
    def draw(self, screen):
        # Card background
        pygame.draw.rect(screen, (40, 40, 40), self.rect, border_radius=8)
        pygame.draw.rect(screen, (100, 100, 100), self.rect, 2, border_radius=8)
        
        # Contract details
        y_offset = self.rect.y + 10
        
        # Route
        route_text = SMALL_FONT.render(f"Route: {self.route}", True, (255, 255, 255))
        screen.blit(route_text, (self.rect.x + 10, y_offset))
        y_offset += 25
        
        # Cargo
        cargo_text = SMALL_FONT.render(f"Cargo: {self.cargo}", True, (200, 200, 200))
        screen.blit(cargo_text, (self.rect.x + 10, y_offset))
        y_offset += 20
        
        # Distance
        distance_text = SMALL_FONT.render(f"Distance: {self.distance} miles", True, (200, 200, 200))
        screen.blit(distance_text, (self.rect.x + 10, y_offset))
        y_offset += 20
        
        # Payment (highlighted)
        payment_text = SMALL_FONT.render(f"Payment: ${self.payment:,}", True, (0, 255, 0))
        screen.blit(payment_text, (self.rect.x + 10, y_offset))
        y_offset += 20
        
        # Deadline
        deadline_text = SMALL_FONT.render(f"Deadline: {self.deadline}h", True, (255, 255, 0))
        screen.blit(deadline_text, (self.rect.x + 10, y_offset))
        
        # Draw the accept button
        self.button.draw(screen)

def contract_selection_demo():
    """Demo of your contract selection screen"""
    # Sample contracts
    contracts = [
        ContractCard(50, 100, "Chicago → Detroit", "Steel Beams", 280, 3500, 8),
        ContractCard(310, 100, "Denver → Phoenix", "Machinery", 450, 5200, 12),
        ContractCard(570, 100, "Seattle → Portland", "Oversize Load", 180, 4800, 6)
    ]
    
    cash = 15000
    selected_contract = None
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Check contract selections
            for i, contract in enumerate(contracts):
                if contract.handle_event(event):
                    selected_contract = i
                    print(f"Selected contract {i + 1}: {contract.route}")
                    # Here you'd transition to the driving game
        
        # Update hover states
        for contract in contracts:
            contract.update(mouse_pos)
        
        # Rendering
        screen.fill((20, 20, 20))
        
        # Title
        title_text = FONT.render("Available Contracts", True, (255, 255, 255))
        screen.blit(title_text, (300, 20))
        
        # Cash display
        cash_text = FONT.render(f"Cash: ${cash:,}", True, (0, 255, 0))
        screen.blit(cash_text, (50, 50))
        
        # Draw contracts
        for contract in contracts:
            contract.draw(screen)
        
        # Selection feedback
        if selected_contract is not None:
            feedback_text = SMALL_FONT.render(f"Contract {selected_contract + 1} selected! Starting delivery...", True, (255, 255, 0))
            screen.blit(feedback_text, (250, 300))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    contract_selection_demo()
