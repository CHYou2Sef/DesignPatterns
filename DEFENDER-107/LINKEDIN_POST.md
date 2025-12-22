# 🚀 Just Deployed: API Defender - A Design Patterns Showcase

I’m excited to share **API Defender**, a space shooter I developed as a technical showcase for **Advanced Design Patterns**! 🎮

We took a classic arcade concept and engineered it using enterprise-grade architecture principles. No spaghetti code here—just clean, modular, and scalable Python.

### 🏗️ Under the Hood: The Architecture
The core challenge was to manage complex game state and behavior without conditioned chaos. Here are the patterns that made it possible:

*   **State Pattern**: The game engine transitions seamlessly between Menu, Gameplay, Pause, and Game Over states, eliminating massive `if/else` blocks in the main loop.
*   **Decorator Pattern**: Player upgrades (Shields, Rapid Fire) are applied as dynamic wrappers around the ship object. This allows for stacking power-ups and clean, recursive removal when they expire.
*   **Composite Pattern**: Enemy swarms ("Squadrons") and individual units ("Hunters", "Drones") are treated uniformly, simplifying the collision and update logic.
*   **Singleton Pattern**: A centralized `APILogger` handles event tracking and asynchronous score submission (deployed with a Flask backend).

### 🌐 Play it on the Web!
Thanks to **WebAssembly (Pygbag)**, this Python/Pygame project is running directly in your browser on Vercel!

👉 **Play Now:** [INSERT_YOUR_VERCEL_LINK_HERE]
*(Note: Runs best on Desktop!)*

### 💻 Tech Stack
*   **Core**: Python 3.12, Pygame-CE
*   **Web Port**: Pygbag (WebAssembly)
*   **Architecture**: Design Patterns (GoF)

Check out the code on GitHub: [INSERT_GITHUB_LINK]

#Python #Pygame #WebAssembly #DesignPatterns #SoftwareArchitecture #GameDev #Coding #Vercel
