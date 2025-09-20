# HH Tycoon
## Pygame Prototype Development Plan

### 🚛 Project Overview
Bu## 🚀 Minimum Viable Product (v0.1)

**Core Features**
- Single map environment with one truck model
- Individual delivery missions (no concurrent contracts)
### Week 1: Foundation Systems

# Heavy Haul Tycoon - Development Log

## 🎯 Project Status: Working Prototype Complete! ✅

Heavy Haul Tycoon is a trucking simulation game built in Python using Pygame. The game features contract-based cargo delivery missions with economic management, fuel consumption, and upgrade systems.

**Current Status**: Fully playable prototype with integrated contract system, driving mechanics, fuel management, and economic progression.

---

## 🚀 Development Journey

### Core Systems Implemented

#### 1. Contract System (`contract_system.py`)
- **Dynamic Route Generation**: Uses `cities.json` for realistic city-to-city routes
- **Economic Model**: Revenue calculations based on distance, cargo type, and deadlines
- **Cargo Types**: Standard (1.1x), Oversize (1.25x), Superload (1.5x) multipliers
- **Payment Formula**: `BASE_RATE_PER_MILE * distance * weight_multiplier + bonuses`
- **Visual Contract Cards**: Clean UI for contract selection with payment breakdowns

#### 2. Driving Mechanics (`integrated_game.py`)
- **Truck Physics**: Realistic acceleration, deceleration, and turning with momentum
- **Fuel System**: Consumption based on speed and driving behavior
- **Road Network**: Multi-lane roads with turns, intersections, and off-road detection
- **Collision Detection**: Bridge hazards with penalty system (non-fatal)
- **Visual Design**: Detailed truck graphics with cab and trailer rendering

#### 3. Fuel Management System
- **Interactive Refueling**: Press R near stations to refuel for $50
- **Strategic Placement**: Fuel stations positioned on main routes
- **Consumption Rate**: 0.008 units per frame (balanced for 5-15 minute missions)
- **Visual Feedback**: Fuel gauge with color-coded warnings

#### 4. Upgrade System Framework (`upgrade_system.py`)
- **Config-Driven**: Uses `config.yml` for easy balance adjustments
- **Three Categories**: Engine (speed), Fuel Tank (capacity), Frame (durability)
- **Progressive Costs**: Exponential pricing for game balance
- **Integration Ready**: Framework prepared for full implementation

#### 5. Complete Game Flow
- **Three-Scene System**: Contracts → Driving → Results
- **State Management**: Persistent cash, fuel, and progress tracking
- **Mission Completion**: Delivery zones with distance-based detection
- **Economic Feedback**: Payment calculations with time bonuses and penalties

### 🔧 Major Technical Achievements

#### Critical Bug Fix: Mission Failure Issue
**Problem**: Missions were ending immediately upon start  
**Root Cause**: String return value `"continue"` was being treated as `True` in boolean context  
**Solution**: 
```python
# Before (buggy)
if mission_complete or elapsed_time > deadline:

# After (fixed)  
mission_ended = (mission_complete == "delivery_complete") or elapsed_time > deadline
```

#### Data-Driven Architecture
- **`cities.json`**: City coordinates enabling dynamic route generation
- **`config.yml`**: Game balance parameters for easy tuning
- **Modular Design**: Systems can be developed and tested independently

#### Performance Optimization
- **Efficient Rendering**: 60 FPS target with optimized drawing calls
- **Smart Collision Detection**: Minimal performance impact
- **Debug System**: Comprehensive logging for development

### 🎮 Current Gameplay Features

#### Contract Selection
- Choose from 3 dynamically generated contracts
- Route information with origin/destination cities
- Payment calculations based on distance and cargo type
- Deadline pressure with time-based bonuses

#### Driving Missions
- **Controls**: WASD/Arrow keys for movement
- **Physics**: Realistic truck handling with momentum
- **Navigation**: Complex road network with multiple paths
- **Hazards**: Bridge collision detection with penalties
- **Fuel Strategy**: Manage consumption and refueling stops

#### Economic System
- **Starting Cash**: $10,000
- **Fuel Cost**: $50 per full tank refuel
- **Revenue Range**: $1,000 - $10,000+ per delivery
- **Time Bonuses**: Reward efficient deliveries
- **Penalty System**: Bridge strikes, late deliveries

### 📊 Game Balance

#### Mission Parameters
- **Deadlines**: 5-15 hours based on distance and difficulty
- **Distance Calculation**: Grid-based using `(|dx| + |dy|) / 10`
- **Fuel Consumption**: Balanced for strategic decision-making
- **Payment Scaling**: Exponential increase for longer/harder routes

#### Economic Progression
- **Base Rate**: $6.00 per mile
- **Cargo Multipliers**: Standard/Oversize/Superload scaling
- **Upgrade Costs**: Progressive pricing prevents easy exploitation
- **Risk/Reward**: High-paying contracts have tighter deadlines

### 🗂️ File Structure
```
hh-tycoon/
├── game/
│   ├── integrated_game.py      # Main game with full flow
│   ├── contract_system.py      # Contract generation demo
│   ├── upgrade_system.py       # Vehicle improvement system
│   └── data/
│       ├── cities.json         # City network data
│       └── config.yml          # Balance parameters
├── README.md                   # This documentation
└── requirements.txt            # Python dependencies
```

### 🛠️ Technical Specifications
- **Engine**: Pygame 2.6.1
- **Python**: 3.13+
- **Dependencies**: pygame, pyyaml
- **Platform**: Cross-platform (developed on Linux)
- **Performance**: Stable 60 FPS with efficient rendering

---

## 🎯 Original Design Vision (Reference)

### Design Philosophy
**Fun Over Realism**: Realistic constraints serve as engaging gameplay elements  
**Quick Gameplay Loops**: 2-4 minute delivery cycles with instant retry  
**Single Core Mechanic Focus**: Master truck handling with fuel pressure first  
**Data-Driven Expansion**: Modular systems for easy content addition

### Economic Framework
**Revenue Formula**:
```
payout = base_rate_per_mile × distance × (1 + weight_factor + oversize_factor) × deadline_multiplier
```

**Penalty Structure**:
- Bridge strike: $5,000 fine (now non-fatal)
- Late delivery: -10% to -50% payment reduction
- Early delivery: +20% time bonus

### Progression System Vision
- **Vehicle Upgrades**: Engine, fuel tank, frame improvements
- **Trailer Unlocks**: Access to higher-value cargo
- **Dynamic Events**: Weather, inspections, breakdowns *(future)*

---

## 🚀 Getting Started

### Prerequisites
```bash
pip install pygame pyyaml
```

### Running the Game
```bash
cd game
python integrated_game.py
```

### Controls
- **Movement**: WASD or Arrow Keys  
- **Contract Selection**: Number keys 1, 2, 3
- **Refuel**: R (when near fuel stations)
- **Navigate**: Follow on-screen prompts

---

## 🎯 Development Status

**Phase**: ✅ **Working Prototype Complete**  
**Next**: Game Design Document and Feature Expansion Planning

### Features Completed ✅
- [x] Contract generation and selection system
- [x] Full truck driving mechanics with physics
- [x] Fuel consumption and refueling stations  
- [x] Complete economic system with payments
- [x] Mission completion detection and scoring
- [x] Results screen with detailed breakdown
- [x] Multi-scene game flow integration
- [x] Visual polish and user interface
- [x] Debug system and performance optimization
- [x] Data-driven configuration system

### Development Insights
1. **Debug-Driven Development**: Extensive logging was critical for solving the mission failure bug
2. **Modular Architecture**: Separate systems enabled independent testing and iteration
3. **Data-Driven Design**: JSON/YAML configuration allows rapid gameplay balancing
4. **Progressive Building**: Implementing one system at a time reduced complexity
5. **User Feedback Integration**: Quick iteration based on immediate gameplay testing

---

*This prototype demonstrates successful system integration, problem-solving methodology, and rapid game development iteration. The foundation is solid for expanding into a full commercial game.*

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