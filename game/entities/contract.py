"""
Contract Entity - Represents delivery contracts
"""
import random
from core.constants import BASE_RATE_PER_MILE

class Contract:
    """Represents a delivery contract with route, cargo, and payment details"""
    
    def __init__(self, origin_city, dest_city, cargo_type, deadline_hours):
        self.origin = origin_city
        self.destination = dest_city
        self.cargo_type = cargo_type
        self.deadline_hours = deadline_hours
        
        # Calculate distance and payment
        dx = abs(dest_city['x'] - origin_city['x'])
        dy = abs(dest_city['y'] - origin_city['y'])
        self.distance_miles = (dx + dy) / 10
        
        # Payment calculation
        weight_multipliers = {'Standard': 1.1, 'Oversize': 1.25, 'Superload': 1.5}
        oversize_bonuses = {'Standard': 0.0, 'Oversize': 0.20, 'Superload': 0.40}
        
        base_payment = BASE_RATE_PER_MILE * self.distance_miles
        weight_factor = weight_multipliers[cargo_type] - 1
        oversize_factor = oversize_bonuses[cargo_type]
        
        # Deadline multiplier
        if deadline_hours <= 4:
            deadline_multiplier = 1.3
        elif deadline_hours <= 6:
            deadline_multiplier = 1.15
        else:
            deadline_multiplier = 1.0
            
        self.payout = int(base_payment * (1 + weight_factor + oversize_factor) * deadline_multiplier)
        
        # Cargo description
        descriptions = {
            'Standard': ['Steel Coils', 'Lumber', 'Electronics'],
            'Oversize': ['Construction Equipment', 'Industrial Machinery'],
            'Superload': ['Wind Turbine Blades', 'Bridge Sections']
        }
        self.cargo_description = random.choice(descriptions[cargo_type])
    
    @property
    def route_text(self):
        """Get formatted route string"""
        return f"{self.origin['name']} → {self.destination['name']}"
    
    def get_deadline_seconds(self):
        """Get deadline in seconds"""
        return self.deadline_hours * 3600
