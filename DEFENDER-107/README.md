# API DEFENDER - Design Patterns Game

A Python/Pygame-based space defender game that demonstrates 4 key design patterns.

## 🎮 Game Overview

**API Defender** is an educational game showcasing design patterns through gameplay mechanics. The objective is to defend against incoming virus attacks while managing power-ups and progressing through levels.

## 🏛️ Design Patterns Implemented

### 1. **SINGLETON Pattern** (The Logger)

- **Class:** `APILogger`
- **Purpose:** Ensures only one instance of the logger exists throughout the game
- **Implementation:** `__new__` method controls instantiation
- **Benefit:** All log events are funneled through a single point, ensuring consistent logging behavior

### 2. **COMPOSITE Pattern** (The Enemies)

- **Classes:** `GameEntity` (abstract), `Virus`, `VirusSwarm`
- **Purpose:** Treat individual enemies and groups of enemies uniformly
- **Implementation:** `VirusSwarm` contains multiple `Virus` objects and delegates operations to all children
- **Benefit:** Simplifies managing complex hierarchies of game objects

### 3. **DECORATOR Pattern** (The Player)

- **Classes:** `Ship` (abstract), `FighterJet`, `RapidFireDecorator`, `ShieldDecorator`, `DoubleShieldDecorator`
- **Purpose:** Add new functionality to the ship dynamically without modifying the original class
- **Implementation:** 
  - `RapidFireDecorator` wraps a `Ship` and adds triple-shot capability with pulsing cyan aura
  - `ShieldDecorator` wraps a `Ship` and adds single-hit protection with blue pulsing bubble
  - `DoubleShieldDecorator` wraps a `Ship` and adds double-hit protection with dual-layer purple/blue shields
- **Benefit:** Flexible runtime feature addition without inheritance bloat, decorators can be stacked
- **Visual Effects:** Each decorator features animated pulsing effects using sine waves for alpha and size variations

### 4. **STATE Pattern** (The Game Flow)

- **Classes:** `GameState` (abstract), `MenuState`, `PlayState`, `GameOverState`
- **Purpose:** Encapsulate different game phases as separate state objects
- **Implementation:** Game transitions between states using `change_state()`
- **Benefit:** Clean separation of game logic for each phase

## 🎯 Game Controls

| Key                  | Action                                        |
| -------------------- | --------------------------------------------- |
| **LEFT/RIGHT Arrow** | Move ship                                     |
| **SPACE**            | Shoot bullets                                 |
| **P**                | Activate Power-Up (Rapid Fire)                |
| **ENTER**            | Start game / Continue to next level / Restart |

## 🚀 Features

- **Progressive Difficulty:** Each level increases enemy count and speed
- **Score Tracking:** Earn 100 points per destroyed enemy
- **Power-Up System:** Activate rapid fire for double shots
- **Level System:** Complete levels by destroying all enemies
- **API Logging:** All events logged to Flask API and local file (`game_logs.txt`)
- **HUD Display:** Real-time score, level, and enemy count

## 📋 Game States

### Menu State

- Shows game title and instructions
- Press ENTER to start

### Play State

- Main gameplay loop
- Destroy enemies before they reach the bottom
- Power-up available (press P)
- Real-time score and level display

### Game Over State

- Shows final score and level reached
- Victory: "LEVEL COMPLETE!" - Press ENTER for next level
- Defeat: "GAME OVER" - Press ENTER to return to menu

## 🔧 Technical Requirements

### Dependencies

```
pygame
flask
requests
```

Install with:

```bash
pip install -r requirements.txt
```

### Running the Game

#### 1. Start the API Server (optional, for logging)

```bash
python server.py
```

#### 2. Run the Game

```bash
python game.py
```

**Note:** The game runs even if the API server is offline (logs are suppressed with a warning).

## 📊 Game Mechanics

### Enemy Behavior

- Viruses move downward at increasing speed per level
- Game ends if any virus reaches the bottom (y > 500)
- Game completes when all viruses destroyed

### Player Mechanics

- BasicShip: Single shot per keypress
- RapidFireDecorator: Double shots (offset +15 pixels)
- Visual indicator (gold border) when power-up active

### Scoring

- +100 points per destroyed enemy
- Levels increase enemy count by 1 per level
- Enemy speed increases by 0.5x per level

## 📝 Logging

All game events are logged to:

- **Console Output:** Via Flask API
- **File Output:** `game_logs.txt` (local storage)

Log levels: `ACTION`, `UPGRADE`, `GAME`, `STATE`, `SYSTEM`

## 🐛 Bug Fixes

### Fixed Issues

1. ✅ **Missing `draw()` method in PlayState** - Now properly implements all abstract methods
2. ✅ **Score tracking** - Added score system with display
3. ✅ **Level progression** - Game now supports multiple levels with increasing difficulty
4. ✅ **Game state management** - Proper state transitions between menu → play → game over

## 🎨 Visual Design

- **Colors:**

  - Blue ship: `(50, 200, 200)`
  - Red enemies: `(200, 50, 50)`
  - Yellow bullets: `(255, 255, 0)`
  - Gold power-up indicator: `(255, 215, 0)`
////////////////////////////////////////////
- **Screen Resolution:** 800x600 pixels
- **Frame Rate:** 60 FPS

## 🎓 Educational Value

This project demonstrates:

- How design patterns solve common OOP problems
- Clean code architecture and separation of concerns
- Game state management
- Event-driven programming
- Pygame library usage
- API integration in games

---

**Course:** Design Patterns (5th Semester)  
**Project:** DEFENDER-107  
**Status:** ✅ Complete and Functional
