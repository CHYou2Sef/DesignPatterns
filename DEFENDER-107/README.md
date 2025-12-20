# 🚀 API Defender V2.4

**API Defender** is a secure, cloud-integrated space shooter built to demonstrate **Advanced Design Patterns** within a real-world Python/Pygame architecture.

![Game Style](https://img.shields.io/badge/Style-Cyberpunk-blueviolet)
![Patterns](https://img.shields.io/badge/Patterns-6%2B-blue)
![Cloud](https://img.shields.io/badge/Cloud-Render-green)

---

## 📖 Project Documentation
For the full technical analysis, diagrams, and pattern breakdowns, please refer to the:
👉 **[FINAL TECHNICAL REPORT (PDF/MD)](FINAL_REPORT.md)**

---

## 🔥 Key V2.4 Features
- **Cloud-Synced Gameplay**: Every action is logged to a remote REST API in real-time.
- **Dynamic Upgrades**: Runtime ship modifications using the **Decorator Pattern**.
- **Interactive Menu**: Full keyboard navigation with Start, Options, and Exit logic.
- **Advanced Physics**: Procedural Asteroid obstacles with rotation and drifting.
- **Visual Polish**: Neon glows, pulsing engines, and glass-panel HUD.
- **Global Leaderboard**: Cross-platform pilot rankings fetched from the cloud.

---

## 🛠️ Architecture (Design Patterns)
The project utilizes 6 major patterns to ensure scalability and clean separation of concerns:

1.  **State Pattern**: Orchestrates Menu, War, Pause, and Victory phases.
2.  **Decorator Pattern**: Dynamically stacks Shields and Rapid-Fire upgrades.
3.  **Composite Pattern**: Manages the hierarchy of Drones and Hazards.
4.  **Singleton Pattern**: Provides a thread-safe global APILogger.
5.  **Strategy Pattern**: Encapsulates varying Power-up behaviors.
6.  **Observer Pattern**: The core event loop handling Pilot input.

---

## 🚀 Quick Start

### 1. Requirements
- Python 3.10+
- Pygame (`pip install pygame`)
- Requests (`pip install requests`)

### 2. Launch
```bash
python main.py
```

### 3. Build Executable
```bash
pyinstaller --noconsole --onefile --name "ApiDefender" main.py
```

---

## 🎮 Controls
- **Mouse**: Steering & Aiming
- **Left Click / Space**: Fire Cannons
- **ESC / P**: Pause Mission
- **ENTER**: Select / Start

---

## 🏆 Project Originality
Unlike traditional clones, **API Defender** treats the game as a data-generating system. The "enemy" isn't just a drone—it's a security threat that triggers high-priority logs to a remote DevOps-style dashboard.

---
**Course:** 5th Semester - Design Patterns  
**Team:** DEFENDER-107  
**Status:** ✅ Production Ready
