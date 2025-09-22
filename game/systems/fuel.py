"""
Fuel Management System
"""
import pygame
from core.constants import FUEL_DRAIN_RATE, REFUEL_COST

class FuelSystem:
    """Manages fuel consumption, refueling, and fuel station interactions"""
    
    def __init__(self):
        self.fuel_stations = [
            {'x': 140, 'y': 210, 'rect': pygame.Rect(100, 180, 80, 60)},
            {'x': 660, 'y': 430, 'rect': pygame.Rect(620, 400, 80, 60)}
        ]
    
    def update_fuel_consumption(self, game_state, truck):
        """Update fuel consumption based on truck speed"""
        if abs(truck.speed) > 0.1:
            consumption = FUEL_DRAIN_RATE * (1 + abs(truck.speed) / 5)
            game_state.fuel -= consumption
            game_state.fuel = max(0, game_state.fuel)
    
    def check_refuel_availability(self, game_state, truck):
        """Check if truck is near a fuel station and can refuel"""
        truck_rect = truck.get_rect()
        
        for station in self.fuel_stations:
            station_zone = station['rect'].inflate(40, 40)
            if station_zone.colliderect(truck_rect):
                game_state.refuel_available = (game_state.fuel < 100)
                return True
        
        game_state.refuel_available = False
        return False
    
    def attempt_refuel(self, game_state):
        """Attempt to refuel if conditions are met"""
        if game_state.refuel_available and game_state.cash >= REFUEL_COST:
            return game_state.refuel_truck(REFUEL_COST)
        return False
    
    def is_out_of_fuel(self, game_state):
        """Check if truck is out of fuel"""
        return game_state.fuel <= 0
    
    def render_fuel_stations(self, screen, fonts):
        """Render fuel stations on the map"""
        from core.constants import LIGHT_GRAY, DARK_GRAY, RED, WHITE
        
        for station in self.fuel_stations:
            # Station building
            pygame.draw.rect(screen, LIGHT_GRAY, station['rect'])
            pygame.draw.rect(screen, DARK_GRAY, station['rect'], 2)
            
            # Fuel pumps
            pump_rect = pygame.Rect(station['rect'].x + 10, station['rect'].bottom, 15, 20)
            pygame.draw.rect(screen, RED, pump_rect)
            pump_rect.x += 45
            pygame.draw.rect(screen, RED, pump_rect)
            
            # Price sign
            price_text = fonts['small'].render("$4.50/gal", True, WHITE)
            screen.blit(price_text, (station['rect'].x, station['rect'].y - 20))
    
    def render_refuel_prompts(self, screen, fonts, game_state, truck):
        """Render refuel prompts when near stations"""
        if not game_state.refuel_available:
            return
        
        truck_rect = truck.get_rect()
        for station in self.fuel_stations:
            station_zone = station['rect'].inflate(40, 40)
            if station_zone.colliderect(truck_rect):
                if game_state.fuel < 100:
                    prompt_text = fonts['normal'].render("Press R to refuel ($50)", True, (255, 255, 0))
                    screen.blit(prompt_text, (truck.x - 60, truck.y - 40))
                else:
                    full_text = fonts['normal'].render("Tank Full", True, (0, 255, 0))
                    screen.blit(full_text, (truck.x - 30, truck.y - 40))
                break