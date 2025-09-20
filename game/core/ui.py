"""
UI components for Heavy Haul Tycoon
Handles HUD elements, menus, and user interface
"""
import pygame
import math

class UIElement:
    """Base UI element class"""
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = True
    
    def update(self, dt):
        pass
    
    def render(self, screen):
        pass

class FuelGauge(UIElement):
    """Enhanced fuel gauge with visual feedback"""
    def __init__(self, x, y, width=200, height=25):
        super().__init__(x, y, width, height)
        self.fuel_percentage = 1.0
        self.max_fuel = 100.0
        self.warning_flash = 0
        
    def update_fuel(self, current_fuel, max_fuel=100.0):
        """Update fuel levels"""
        self.fuel_percentage = max(0, min(1, current_fuel / max_fuel))
        self.max_fuel = max_fuel
        
    def update(self, dt):
        """Update animations"""
        if self.fuel_percentage <= 0.25:
            self.warning_flash += dt * 8  # Flash when low
    
    def render(self, screen, font):
        """Render the fuel gauge"""
        # Background
        pygame.draw.rect(screen, (60, 60, 60), self.rect, border_radius=4)
        
        # Fuel bar
        fuel_width = self.fuel_percentage * (self.rect.width - 4)
        fuel_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 2, 
                               fuel_width, self.rect.height - 4)
        
        # Color based on fuel level
        if self.fuel_percentage > 0.5:
            fuel_color = (0, 200, 0)  # Green
        elif self.fuel_percentage > 0.25:
            fuel_color = (255, 255, 0)  # Yellow
        else:
            # Red, flashing when very low
            flash_intensity = abs(math.sin(self.warning_flash))
            fuel_color = (255, int(100 + 155 * flash_intensity), 0)
        
        pygame.draw.rect(screen, fuel_color, fuel_rect, border_radius=3)
        
        # Border
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=4)
        
        # Text
        fuel_text = font.render(f"Fuel: {self.fuel_percentage * 100:.1f}%", True, (255, 255, 255))
        screen.blit(fuel_text, (self.rect.right + 10, self.rect.y + 2))

class Speedometer(UIElement):
    """Speed indicator with visual gauge"""
    def __init__(self, x, y, max_speed=5.0):
        super().__init__(x, y, 120, 25)
        self.current_speed = 0
        self.max_speed = max_speed
        
    def update_speed(self, speed):
        """Update current speed"""
        self.current_speed = abs(speed)
    
    def render(self, screen, font):
        """Render speedometer"""
        # Background
        pygame.draw.rect(screen, (60, 60, 60), self.rect, border_radius=4)
        
        # Speed bar
        speed_percentage = min(1.0, self.current_speed / self.max_speed)
        speed_width = speed_percentage * (self.rect.width - 4)
        speed_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 2,
                                speed_width, self.rect.height - 4)
        
        # Color based on speed
        if speed_percentage < 0.5:
            speed_color = (0, 255, 0)  # Green
        elif speed_percentage < 0.8:
            speed_color = (255, 255, 0)  # Yellow
        else:
            speed_color = (255, 100, 0)  # Orange
            
        pygame.draw.rect(screen, speed_color, speed_rect, border_radius=3)
        
        # Border
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=4)
        
        # Text
        speed_text = font.render(f"Speed: {self.current_speed:.1f} mph", True, (255, 255, 255))
        screen.blit(speed_text, (self.rect.right + 10, self.rect.y + 2))

class Timer(UIElement):
    """Mission timer display"""
    def __init__(self, x, y):
        super().__init__(x, y, 150, 25)
        self.elapsed_time = 0
        self.deadline = None
        self.warning = False
        
    def start_mission(self, deadline_hours):
        """Start a new mission timer"""
        self.elapsed_time = 0
        self.deadline = deadline_hours * 60  # Convert to seconds
        self.warning = False
    
    def update(self, dt):
        """Update timer"""
        if self.deadline:
            self.elapsed_time += dt
            # Warning when 80% of time used
            self.warning = self.elapsed_time / self.deadline > 0.8
    
    def get_time_remaining(self):
        """Get remaining time in seconds"""
        if self.deadline:
            return max(0, self.deadline - self.elapsed_time)
        return 0
    
    def render(self, screen, font):
        """Render timer"""
        if self.deadline:
            remaining = self.get_time_remaining()
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            
            color = (255, 100, 100) if self.warning else (255, 255, 255)
            timer_text = font.render(f"Time: {minutes:02d}:{seconds:02d}", True, color)
            screen.blit(timer_text, (self.rect.x, self.rect.y))

class ObjectiveArrow(UIElement):
    """Arrow pointing to destination"""
    def __init__(self, x, y):
        super().__init__(x, y, 100, 30)
        self.target_x = 0
        self.target_y = 0
        self.player_x = 0
        self.player_y = 0
        
    def set_target(self, target_x, target_y):
        """Set the target destination"""
        self.target_x = target_x
        self.target_y = target_y
    
    def update_player_position(self, player_x, player_y):
        """Update player position for arrow calculation"""
        self.player_x = player_x
        self.player_y = player_y
    
    def render(self, screen, font):
        """Render objective arrow and distance"""
        # Calculate direction to target
        dx = self.target_x - self.player_x
        dy = self.target_y - self.player_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 10:  # Only show if not at destination
            angle = math.atan2(dy, dx)
            
            # Arrow position (center of UI element)
            arrow_x = self.rect.centerx
            arrow_y = self.rect.centery
            
            # Draw arrow
            arrow_length = 15
            end_x = arrow_x + math.cos(angle) * arrow_length
            end_y = arrow_y + math.sin(angle) * arrow_length
            
            # Arrow line
            pygame.draw.line(screen, (255, 255, 0), (arrow_x, arrow_y), (end_x, end_y), 3)
            
            # Arrowhead
            head_angle1 = angle + math.pi * 0.8
            head_angle2 = angle - math.pi * 0.8
            head_length = 8
            
            head1_x = end_x + math.cos(head_angle1) * head_length
            head1_y = end_y + math.sin(head_angle1) * head_length
            head2_x = end_x + math.cos(head_angle2) * head_length
            head2_y = end_y + math.sin(head_angle2) * head_length
            
            pygame.draw.polygon(screen, (255, 255, 0), [
                (end_x, end_y), (head1_x, head1_y), (head2_x, head2_y)
            ])
            
            # Distance text
            distance_text = font.render(f"Distance: {distance/10:.1f} mi", True, (255, 255, 255))
            screen.blit(distance_text, (self.rect.x, self.rect.y + 35))

class HUD:
    """Main heads-up display"""
    def __init__(self, engine):
        self.engine = engine
        self.font = engine.get_font('medium')
        
        # UI Components
        self.fuel_gauge = FuelGauge(20, 20)
        self.speedometer = Speedometer(20, 55)
        self.timer = Timer(20, 90)
        self.objective_arrow = ObjectiveArrow(650, 20)
        self.cash_display_pos = (20, 125)
        
        # Status messages
        self.status_messages = []
        self.message_duration = 3.0  # seconds
    
    def update(self, dt, player_data, truck=None):
        """Update HUD elements"""
        # Update fuel gauge
        self.fuel_gauge.update_fuel(player_data['fuel'])
        self.fuel_gauge.update(dt)
        
        # Update speedometer
        if truck:
            self.speedometer.update_speed(truck.speed)
            self.objective_arrow.update_player_position(truck.x, truck.y)
        
        # Update timer
        self.timer.update(dt)
        
        # Update status messages
        for message in self.status_messages[:]:
            message['time'] -= dt
            if message['time'] <= 0:
                self.status_messages.remove(message)
    
    def add_status_message(self, text, color=(255, 255, 255), duration=3.0):
        """Add a temporary status message"""
        self.status_messages.append({
            'text': text,
            'color': color,
            'time': duration
        })
    
    def set_destination(self, dest_x, dest_y):
        """Set the delivery destination"""
        self.objective_arrow.set_target(dest_x, dest_y)
    
    def start_mission(self, deadline_hours):
        """Start a new delivery mission"""
        self.timer.start_mission(deadline_hours)
    
    def render(self, screen):
        """Render all HUD elements"""
        # Main UI components
        self.fuel_gauge.render(screen, self.font)
        self.speedometer.render(screen, self.font)
        self.timer.render(screen, self.font)
        self.objective_arrow.render(screen, self.font)
        
        # Cash display
        cash_text = self.font.render(f"Cash: ${self.engine.player_data['cash']:,}", 
                                   True, (0, 255, 0))
        screen.blit(cash_text, self.cash_display_pos)
        
        # Status messages
        y_offset = 200
        for message in self.status_messages:
            msg_text = self.font.render(message['text'], True, message['color'])
            # Semi-transparent background
            bg_rect = msg_text.get_rect()
            bg_rect.x = 20
            bg_rect.y = y_offset
            bg_rect.inflate_ip(10, 5)
            
            bg_surface = pygame.Surface(bg_rect.size)
            bg_surface.fill((0, 0, 0))
            bg_surface.set_alpha(128)
            screen.blit(bg_surface, bg_rect)
            
            screen.blit(msg_text, (25, y_offset + 2))
            y_offset += 30

class Button(UIElement):
    """Clickable button"""
    def __init__(self, x, y, width, height, text, font, 
                 color=(100, 100, 100), text_color=(255, 255, 255)):
        super().__init__(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.text_color = text_color
        self.hovered = False
        self.clicked = False
        
    def handle_event(self, event):
        """Handle mouse events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.clicked = True
                return True
        return False
    
    def update(self, dt):
        """Update button state"""
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)
        
    def render(self, screen):
        """Render button"""
        # Change color when hovered
        color = tuple(min(255, c + 50) for c in self.color) if self.hovered else self.color
        
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2, border_radius=5)
        
        # Center text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
