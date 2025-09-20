# HH Tycoon
## Pygame Prototype Development Plan

### 🚛 Project Overview
Bu## 🚀 Minimum Viable Product (v0.1)

**Core Features**
- Single map environment with one truck model
- Individual delivery missions (no concurrent contracts)
### Week 1: Foundation Systems

***Day 5: Fuel Infrastructure**
- [ ] Fuel station placement and interaction zones
- [ ] Refueling mechanics with cost calculations
- [ ] Towing system for fuel depletion scenarios  
- **Success Criteria**: Strategic fuel management affects profitability: Core Framework**
- [ ] Repository initialization and project structure  
- [ ] 60 FPS game loop with stable delta timing
- [ ] Basic fuel management and movement controls
- **Success Criteria**: Responsive truck movement with fuel consumptionfuel management and collision detection
- Single low-bridge hazard implementation
- Contract selection board with 3 simultaneous options
- Mission results screen displaying earnings, penalties, and cash balance

## 🎮 Controls & User Experience

**Input Schema**
- Movement: Arrow keys or WASD
- Navigation: Mouse for menu interactions

**HUD Elements**
- Real-time fuel gauge
- Current speed indicator
- Mission timer
- Cash balance display
- Objective direction indicator

**Feedback Systems**
- Clear failure messages ("Bridge clearance exceeded!", "Fuel depleted - towing fee: $X")
- Immediate visual confirmation of player actions
- Rapid restart capability for failed missions arcade-style logistics game with a satisfying contracts → deliver → upgrade loop. This prototype will serve as the foundation for a future Android release, focusing on core mechanics over feature completeness.

### 🎯 Design Philosophy

**Fun Over Realism**  
Realistic constraints (low bridges, fuel management, regulatory fines) serve as engaging gameplay elements rather than tedious bureaucracy.

**Quick Gameplay Loops**  
- 2-4 minute delivery cycles
- Instant retry capability
- Clear visual feedback on profit margins

**Single Core Mechanic Focus**  
Master top-down truck handling with fuel pressure mechanics first. All other systems build upon this foundation.

**Data-Driven Expansion**  
Contracts, upgrades, and events use modular data structures for easy content addition.

### � Core Gameplay Loop

1. **Contract Selection**: Choose from 3 available jobs (route, cargo weight, deadline, payment)
2. **Delivery Mission**: Navigate top-down driving challenges (roads, hazards, fuel management)
3. **Performance Evaluation**: Receive payments, time bonuses, and penalty assessments
4. **Fleet Improvement**: Invest in speed, fuel capacity, durability upgrades, and trailer unlocks

## 🎮 Game Systems Design

### Economic Framework

**Starting Resources**
- Initial capital: $10,000
- Base truck cost: $8,000 - $20,000
- Fuel pricing: $4.50/gallon

**Revenue Formula**
```
payout = base_rate_per_mile × distance × (1 + weight_factor + oversize_factor) × deadline_multiplier
```

**Penalty Structure**
- Collision damage: $250 per incident
- Bridge strike: Mission failure + $5,000 fine
- Performance bonuses: +20% for early delivery, -10% to -50% for late delivery

### Contract Generation System

**Route Planning**
- Select origin and destination from predefined city network
- Calculate grid-based distance (pathfinding implementation postponed)

**Cargo Classifications**
- **Standard**: Base difficulty and pay rate
- **Oversize**: Increased hazards and 25% pay bonus
- **Superload**: Maximum difficulty and 50% pay bonus

**Deadline Pressure**
- Short deadlines: Higher risk, increased compensation
- Standard deadlines: Balanced risk/reward ratio

### Driving Mechanics

**Core Systems**
- Top-down perspective with tile-based road network
- Off-road penalties (speed reduction and fines)
- Environmental hazards and infrastructure constraints

**Challenge Elements**
- Low bridges (instant mission failure)
- Weigh stations (mandatory stops or fine risk)
- Traffic obstacles (slalom navigation required)
- Fuel consumption tied to throttle usage and time

### Progression System

**Vehicle Upgrades**
- **Engine**: Enhanced top speed and acceleration
- **Fuel Tank**: Increased capacity for longer routes
- **Frame**: Improved durability and reduced collision penalties
- **Trailer Unlocks**: Access to higher-value cargo contracts

**Dynamic Events** *(Future Implementation)*
- Weather-based speed modifiers
- Regulatory inspections
- Mechanical breakdowns and repairs

🎮 MVP Scope (v0.1)

One map (single level), one truck, one delivery at a time.

Fuel bar, simple collision boxes, one low-bridge hazard.

Contract board with 3 choices.

Result screen with payout, fines, cash total.

🕹️ Controls & UX

Arrows/WASD to steer & move.

HUD: fuel bar, speed, timer, cash, mini-objective arrow.

Fail fast: clear messages (“Bridge too low!” / “Out of fuel → towed: $X”).

## � Project Architecture

```
heavy-haul-tycoon-lite/
├── game/
│   ├── main.py                 # Application entry point
│   ├── core/
│   │   ├── engine.py          # Game loop and scene management
│   │   ├── ecs.py             # Entity-component system (optional)
│   │   └── ui.py              # HUD and interface components
│   ├── systems/
│   │   ├── contracts.py       # Job generation and payout formulas
│   │   ├── economy.py         # Financial calculations and progression
│   │   ├── driving.py         # Input handling, movement, collision detection
│   │   └── fuel.py            # Fuel consumption and refueling mechanics
│   ├── data/
│   │   ├── cities.json        # City network and route definitions
│   │   └── config.yml         # Game balance parameters
│   └── assets/
│       ├── sprites/           # Placeholder graphics
│       └── fonts/             # Typography resources
└── README.md
```

## 🧪 Prototype Implementation

### Basic Movement and Fuel System

```python
# game/main.py
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
```

**Implementation Priority**: Deploy this foundation first to validate input responsiveness, frame timing, and core pressure mechanics.

## 📈 Development Roadmap (2-Week Sprint)
*Estimated effort: 10-16 hours*
Day 1 — Core Loop & Feel

 New repo + skeleton.

 Starter loop (above), 60 FPS stable, delta time in place.

 Fuel bar + movement tuning (speed, friction if desired).
Exit criteria: Moving truck drains fuel and “feels responsive”.

**Day 2: Environment & Collision**
- [ ] Road network implementation (rectangle-based)
- [ ] Off-road detection and penalties  
- [ ] Low bridge hazard zones with collision detection
- **Success Criteria**: Complete short delivery route avoiding bridge hazard

**Day 3: Interface & Navigation**
- [ ] HUD implementation (timer, cash, speed indicators)
- [ ] Destination marker and completion detection
- [ ] Results screen with performance evaluation
- **Success Criteria**: End-to-end delivery from point A to B with feedback

**Day 4: Economy Integration**
- [ ] Contract generation system (3 simultaneous offers)
- [ ] Economic calculations (payouts, penalties, bonuses)
- [ ] Persistent cash system across deliveries
- **Success Criteria**: Contract selection influences earnings

Day 5 — Fuel Stops & Tow

 Add fuel stations (enter area to refuel, cost = gallons * price).

 Out-of-fuel → tow to nearest station, flat fee.
Exit: Real fuel decisions matter; towing stings but isn’t game-ending.

**Day 6: Progression Mechanics**
- [ ] Vehicle upgrade system (engine, tank, frame)
- [ ] Tiered pricing and performance improvements
- [ ] Upgrade persistence between sessions
- **Success Criteria**: Noticeable performance improvements from upgrades

Day 7 — Polish & Balancing

 Tune numbers (par times, payouts, fines).

 Add simple SFX placeholders.

 Minimal juice: screen shake on collision; glow on bridge zones.

Week 2 (Stretch, if time)

Pathfinding-lite: weighted grid to place hazards intelligently.

Events: weigh station (stop or risk fine), rain (reduced traction).

Trailer unlocks: gates higher-pay contracts behind upgrades.

Save/Load: JSON save for cash/upgrades/unlocked jobs.

## ⚖️ Game Balance Parameters

### Economic Constants *(Adjustable)*

| Parameter | Value | Description |
|-----------|-------|-------------|
| **Base Rate** | $6.00/mile | Foundation payment calculation |
| **Distance Calculation** | `(|dx| + |dy|) / 10` | Grid-based prototype distance |
| **Weight Multipliers** | Standard: 1.1x<br>Oversize: 1.25x<br>Superload: 1.5x | Cargo difficulty scaling |
| **Oversize Bonus** | 0% / 20% / 40% | Additional complexity compensation |
| **Deadline Multiplier** | 1.0 - 1.3x | Time pressure incentive |
| **Collision Fine** | $250 | Per-incident penalty |
| **Bridge Strike** | Mission fail + $5,000 | Critical infrastructure damage |
| **Fuel Capacity** | 100 → 200 → 300 gallons | Upgrade progression tiers |
| **Fuel Consumption** | 0.05/frame | Base drain rate (60 FPS) |
| **Refuel Cost** | $4.50/gallon | Market price simulation |
| **Towing Fee** | $750 | Emergency service cost |

## 🗺️ Game Content Data

### City Network Configuration
```json
{
  "cities": [
    {"name": "Tampa", "x": 100, "y": 420},
    {"name": "Atlanta", "x": 240, "y": 280},
    {"name": "Dallas", "x": 120, "y": 360},
    {"name": "Phoenix", "x": 60, "y": 380}
  ]
}
```

## � Android Deployment Strategy

### Build Environment Setup
When the PC prototype demonstrates solid gameplay mechanics, deploy to Android using Buildozer:

```bash
# System dependencies
sudo apt update
sudo apt install python3-pip git zip unzip openjdk-17-jdk

# Buildozer installation
pip install buildozer

# Project configuration
cd hh-tycoon-lite/game
buildozer init
```

### Build Configuration
In `buildozer.spec`, configure:
```ini
requirements = python3,pygame
```

### Deployment Commands
```bash
# Debug build
buildozer -v android debug

# Deploy to device (USB debugging enabled)
buildozer android deploy run
```

### Fallback Strategy
If pygame packaging encounters compatibility issues, migrate to Kivy framework while preserving core game logic and shipping capability.