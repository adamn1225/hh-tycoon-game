"""
Game State Management
"""
from core.constants import STARTING_CASH, STARTING_FUEL

class GameState:
    """Manages the overall game state across scenes"""
    
    def __init__(self):
        self.cash = STARTING_CASH
        self.fuel = STARTING_FUEL
        self.current_contract = None
        self.scene = "contracts"  # contracts, driving, results
        self.mission_start_time = 0
        self.mission_penalties = []
        self.mission_completed = False
        
        # Scene transition data
        self.last_mission_time = 0
        self.last_time_bonus = 0
        self.last_penalties = []
        
        # Mission flags
        self.bridge_penalty_applied = False
        self.off_road_warning_time = 0
        self.refuel_available = False
        
        # Generated content
        self.available_contracts = []
    
    def reset_mission_state(self):
        """Reset mission-specific state variables"""
        self.mission_completed = False
        self.mission_penalties = []
        self.bridge_penalty_applied = False
        self.off_road_warning_time = 0
        self.refuel_available = False
    
    def complete_mission(self, mission_time, time_bonus, penalties):
        """Complete the current mission and update state"""
        self.last_mission_time = mission_time
        self.last_time_bonus = time_bonus
        self.last_penalties = penalties
        
        if self.mission_completed:
            actual_payment = self.current_contract.payout + time_bonus - sum(penalties)
            self.cash += actual_payment
            return actual_payment
        return 0
    
    def refuel_truck(self, cost=50):
        """Refuel the truck if player has enough cash"""
        if self.cash >= cost and self.fuel < 100:
            self.fuel = 100.0
            self.cash -= cost
            return True
        return False
    
    def switch_scene(self, new_scene):
        """Switch to a new game scene"""
        self.scene = new_scene
