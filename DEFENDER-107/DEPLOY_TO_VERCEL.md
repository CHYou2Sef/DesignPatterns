# Deploying API Defender to Vercel

Since **API Defender** is a Python/Pygame application, it cannot run natively on Vercel's standard serverless environment. However, we have successfully compiled it to **WebAssembly** using `pygbag`, creating a static web version that Vercel *can* host!

## Option 1: The "Drag & Drop" Method (Fastest)

1.  Navigate to the `build/web` directory in your project folder:
    `y:\ENICar\cours\5th Sem\DesignPatterns\DEFENDER-107\build\web`
2.  Go to [Vercel.com](https://vercel.com) and log in.
3.  Click **"Add New..."** -> **"Project"**.
4.  Drag the `web` folder from your file explorer directly onto the Vercel upload area.
5.  Name the project (e.g., `api-defender-game`) and click **Deploy**.
6.  **Done!** Vercel will give you a URL like `https://api-defender-game.vercel.app`.

## Option 2: GitHub Integration (Recommended for Updates)

1.  **Commit the Build:**
    Ensure the `build/web` folder is included in your git commit. (Check your `.gitignore` if it's not showing up).
    
    ```bash
    git add build/web
    git commit -m "Add web build for Vercel"
    git push
    ```

2.  **Configure Vercel:**
    - Go to Vercel Dashboard -> **Add New...** -> **Project**.
    - Import your `DEFENDER-107` repository.
    - **Framework Preset:** select `Other`.
    - **Root Directory:** Click `Edit` and entering `DEFENDER-107/build/web`.
    - Click **Deploy**.

## Important Notes

- **Performance:** The first load might take a few seconds as it downloads the Python runtime (~10MB).
- **Audio:** Browser policies require the user to interact (click/tap) with the page before audio plays.
- **Networking:** The online leaderboard and logging features are currently disabled in the Web version to prevent crashes (browsers don't allow direct socket connections).

## Troubleshooting

### 1. Black Screen / Game Not Starting?
If the screen is black and the console says `MEDIA USER ACTION REQUIRED`, **click anywhere on the black window**.
*   **Why?** Modern browsers block audio from playing automatically. The game is paused waiting for your permission to start the sound engine.

### 2. 404 Not Found
Ensure your Vercel **Root Directory** is set to `DEFENDER-107/build/web`.
