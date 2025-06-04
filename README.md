# Colouring Game 3 Auto-Clicker

This program automatically clicks all unfilled boxes in the game "Colouring Game 3" using a fast, grid-based approach. It works on multi-monitor setups and skips already-filled boxes for maximum efficiency.

## Features
- **Grid-based clicking:** Clicks the center of every 10x10 box in the game area.
- **Skips filled boxes:** Only clicks boxes that are not already filled (using color variance detection).
- **Multi-monitor support:** Select which monitor to capture from.
- **Configurable click delay:** Set how fast the clicks happen.
- **Global hotkeys:**
  - `F6` to start
  - `F7` to stop
- **No OCR or Tesseract required!**

## Requirements
- Python 3.7 or higher
- Install dependencies:
  ```
  pip install pyautogui opencv-python numpy keyboard mss
  ```

## Setup
1. Place the script in a folder.
2. Install the requirements above.
3. Run the script:
   ```
   python grey_square_clicker.py
   ```

## Usage
1. **Select the game window** and the correct monitor in the GUI.
2. **Set the click delay** (e.g., 0.01 for fast, 0 for fastest; increase if your system/game lags).
3. **Click Start** or press `F6` to begin auto-clicking.
4. **Click Stop** or press `F7` to stop at any time.
5. The program will click every possible 10x10 box in the game area, skipping filled boxes.

## Notes
- The program automatically refreshes the screenshot every 2 seconds for best accuracy.
- The crop region is set for a game window at (232, 65) with size 1499x958. Adjust in the script if your game window is different.
- The program is designed for games where each clickable box is 10x10 pixels and arranged in a grid.

## Troubleshooting
- If clicks are not aligned, check the crop region and box size in the script.
- If the program skips boxes that should be clicked, try lowering the variance threshold in the script (default is 30).
- If the program is too fast/slow, adjust the click delay in the GUI.

## License
MIT 