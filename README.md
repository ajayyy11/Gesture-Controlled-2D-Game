# Gesture-Controlled 2D Game

A Python 2D game that combines Pygame gameplay with camera-based hand tracking and gesture recognition. The project explores touch-free interaction using computer vision.

## Features

- 2D gameplay with player movement, enemies, projectiles, collisions, and scoring
- Hand-landmark tracking for gesture-based input
- Menu and high-score support
- Real-time camera-based interaction

## Tech Stack

- Python
- Pygame
- MediaPipe
- OpenCV
- NumPy

## Requirements

- Python version compatible with the pinned packages in `requirements.txt`
- Webcam for gesture controls
- The MediaPipe hand-landmarker model file included in the repository

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/ajayyy11/Gesture-Controlled-2D-Game.git
   cd Gesture-Controlled-2D-Game
   ```

2. Create and activate a virtual environment.

   **Windows:**
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   **macOS/Linux:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Start the game:

   ```bash
   python main.py
   ```

Allow camera access when prompted. If the camera is unavailable, check operating-system permissions and ensure another application is not using it.

## Project Files

| File | Purpose |
| --- | --- |
| `main.py` | Main gameplay loop and game state |
| `hand_control.py` | Hand tracking and gesture input |
| `menu.py` | Menu interface |
| `assets/` | Game assets |
| `hand_landmarker.task` | Hand-landmarker model |
| `highscore.json` | Local high-score data |

## Development Notes

- Keep dependencies portable; avoid machine-specific paths in requirements files.
- Install only one OpenCV wheel in a virtual environment. This repository uses the contrib wheel, which also provides the `cv2` module.
- Generated Python cache files should not be committed.
- Test camera initialization and gesture handling on the target operating system.

## Author

Ajay Shanmuga Sundaram
