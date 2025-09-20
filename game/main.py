import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
FONT = pygame.font.SysFont(None, 24)

# Game state
truck = pygame.Rect(400, 300, 50, 30)
speed = 3.0
fuel = 100.0
fuel_drain_rate = 0.05  # Per frame at 60 FPS

def render_fuel_gauge(current_fuel):
    """Draw fuel gauge with background and current level"""
    gauge_bg = pygame.Rect(20, 20, 200, 20)
    fuel_width = max(0, current_fuel * 2)
    fuel_bar = pygame.Rect(20, 20, fuel_width, 20)
    
    pygame.draw.rect(screen, (60, 60, 60), gauge_bg, border_radius=4)
    pygame.draw.rect(screen, (0, 200, 0), fuel_bar, border_radius=4)

def main_loop():
    global fuel
    running = True
    
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Input processing
        keys = pygame.key.get_pressed()
        movement_detected = False
        
        if fuel > 0:
            if keys[pygame.K_LEFT]:
                truck.x -= speed
                movement_detected = True
            if keys[pygame.K_RIGHT]:
                truck.x += speed
                movement_detected = True
            if keys[pygame.K_UP]:
                truck.y -= speed
                movement_detected = True
            if keys[pygame.K_DOWN]:
                truck.y += speed
                movement_detected = True
            
            # Fuel consumption during movement
            if movement_detected:
                fuel -= fuel_drain_rate
        
        # Rendering
        screen.fill((20, 20, 20))
        pygame.draw.rect(screen, (200, 0, 0), truck)
        render_fuel_gauge(fuel)
        
        # Fuel depletion feedback
        if fuel <= 0:
            warning_text = FONT.render(
                "Fuel depleted! Towing service required.", 
                True, 
                (220, 220, 220)
            )
            screen.blit(warning_text, (20, 50))
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_loop()
