"""
Data Loading Utilities
"""
import json
import random
from entities.contract import Contract

def load_cities():
    """Load city data from JSON file"""
    try:
        with open('data/cities.json', 'r') as f:
            return json.load(f)['cities']
    except FileNotFoundError:
        # Fallback data if file not found
        return [
            {"name": "Tampa", "x": 100, "y": 420},
            {"name": "Atlanta", "x": 240, "y": 280},
            {"name": "Dallas", "x": 120, "y": 360},
            {"name": "Phoenix", "x": 60, "y": 380}
        ]

def generate_contracts(cities, num=3):
    """Generate contracts using city data"""
    contracts = []
    cargo_types = ['Standard', 'Oversize', 'Superload']
    
    for _ in range(num):
        origin = random.choice(cities)
        destinations = [c for c in cities if c['name'] != origin['name']]
        destination = random.choice(destinations)
        
        cargo_type = random.choices(cargo_types, weights=[0.5, 0.3, 0.2])[0]
        
        # Calculate deadline based on distance
        distance = ((abs(destination['x'] - origin['x']) + abs(destination['y'] - origin['y'])) / 10)
        base_time = max(3, int(distance / 15))  # More generous time
        deadline = base_time + random.randint(2, 6)  # More generous buffer
        deadline = max(5, min(15, deadline))  # At least 5 hours, up to 15
        
        contract = Contract(origin, destination, cargo_type, deadline)
        contracts.append(contract)
    
    return contracts
