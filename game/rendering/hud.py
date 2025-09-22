"""
HUD Rendering System
"""
import pygame
import math
from core.constants import *

class HUD:
    """Handles all HUD element rendering"""
    
    def __init__(self, fonts):
        self.fonts = fonts
    
    def render_fuel_gauge(self, screen, game_state, x=20, y=20):
        """Render fuel gauge"""
        fuel_bg = pygame.Rect(x, y, 200, 25)
        fuel_percent = game_state.fuel / 100
        fuel_width = fuel_percent * 196
        fuel_bar = pygame.Rect(x + 2, y + 2, fuel_width, 21)
        
        pygame.draw.rect(screen, DARK_GRAY, fuel_bg, border_radius=4)
        if fuel_percent > 0.5:
            fuel_color = GREEN
        elif fuel_percent > 0.25:
            fuel_color = YELLOW
        else:
            fuel_color = RED
        
        pygame.draw.rect(screen, fuel_color, fuel_bar, border_radius=3)
        pygame.draw.rect(screen, WHITE, fuel_bg, 2, border_radius=4)
        
        fuel_text = self.fonts['normal'].render(f"Fuel: {game_state.fuel:.1f}%", True, WHITE)
        screen.blit(fuel_text, (x + 210, y + 2))
    
    def render_speed_indicator(self, screen, truck, on_road=True, x=20, y=55):
        """Render speed indicator with off-road warning"""
        speed_color = WHITE if on_road else ORANGE
        speed_text = self.fonts['normal'].render(f"Speed: {abs(truck.speed):.1f} mph", True, speed_color)
        screen.blit(speed_text, (x, y))
        
        if not on_road:
            offroad_indicator = self.fonts['normal'].render("OFF-ROAD", True, ORANGE)
            screen.blit(offroad_indicator, (x + 130, y))
    
    def render_cash(self, screen, game_state, x=20, y=85):
        """Render cash display"""
        cash_text = self.fonts['normal'].render(f"Cash: ${game_state.cash:,}", True, GREEN)
        screen.blit(cash_text, (x, y))
    
    def render_mission_timer(self, screen, game_state, elapsed_time, x=20, y=115):
        """Render mission timer"""
        time_remaining = max(0, game_state.current_contract.get_deadline_seconds() - elapsed_time)
        minutes = int(time_remaining // 60)
        seconds = int(time_remaining % 60)
        timer_color = RED if time_remaining < 120 else WHITE
        timer_text = self.fonts['normal'].render(f"Time: {minutes:02d}:{seconds:02d}", True, timer_color)
        screen.blit(timer_text, (x, y))
    
    def render_distance_to_destination(self, screen, truck, dest_x, dest_y, x=20, y=145):
        """Render distance to destination"""
        distance = math.sqrt((truck.x - dest_x) ** 2 + (truck.y - dest_y) ** 2)
        dist_text = self.fonts['normal'].render(f"Distance: {distance/10:.1f} mi", True, WHITE)
        screen.blit(dist_text, (x, y))
    
    def render_contract_info(self, screen, game_state, x=20, y=175):
        """Render current contract information"""
        contract_text = self.fonts['normal'].render(f"Delivering: {game_state.current_contract.cargo_description}", True, WHITE)
        screen.blit(contract_text, (x, y))
    
    def render_driving_hud(self, screen, game_state, truck, elapsed_time, dest_x, dest_y, on_road=True):
        """Render complete driving HUD"""
        self.render_fuel_gauge(screen, game_state)
        self.render_speed_indicator(screen, truck, on_road)
        self.render_cash(screen, game_state)
        self.render_mission_timer(screen, game_state, elapsed_time)
        self.render_distance_to_destination(screen, truck, dest_x, dest_y)
        self.render_contract_info(screen, game_state)
