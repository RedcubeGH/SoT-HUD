# SoT-HUD
![Downloads](https://img.shields.io/github/downloads/RedcubeGH/SoT-HUD/total)

Author: Redcube

SoT HUD is a fully external Code of Conduct compliant HUD overlay for Sea of Thieves, built using PyQt5, glfw and ImGui for python version 3.11.

The program uses pixel scanning to update the overlay based on the in-game HUD which is then placed ontop of the pre-existing HUD.

The program doesn't interact with the Sea of Thieves Client at all except for Screen Capture and overlaying images on it which are both Code of Conduct compliant due to OBS and Crosshair X working the same.

Based on my interpretation of the Code of Conduct this software is safe to use without the risk of getting banned but Rare refuses to answer me with definite confirmation.

<br>

## Installation

### Option 1: Run from source

1. Ensure **Python 3.11** is installed.
2. Install the required dependencies:

   ```bash
   py -3.11 -m pip install pillow pywin32 keyboard pyqt5 glfw pyimgui PyOpenGL watchdog windows-capture
   ```
3. Run the program:

   ```bash
   py -3.11 'Script/SoT HUD.py'
   ```

### Option 2: Run the compiled release

Download and extract the latest [**release build**](https://github.com/RedcubeGH/SoT-HUD/releases), then run:

```
SoT HUD.exe
```

> **Note:**
>
> * Do not launch SoT HUD while Easy Anti-Cheat (EAC) is initializing, as this can cause the overlay to scale incorrectly. Start SoT HUD either before or after starting the game, if you did start it during EAC initialization just restart it. 
> * SoT HUD is optimized for **fullscreen mode**. Running in windowed mode may cause alignment issues.
---
<br>

## Hotkeys

| Key        | Action                              |
| ---------- | ----------------------------------- |
| **Insert** | Toggle the ImGui configuration menu |
| **Delete** | Exit SoT HUD and save configuration |

<br>

## Customization

The ImGui interface allows full customization of the HUD elements, including colours, font, position, and display options.

To use pre-made or shared configurations:

1. Download a configuration `.zip` file from the [Paks Discord](https://discord.gg/swm3jwrN6M).
2. Place it inside the `YourConfigs/` directory.
3. In the ImGui menu, go to:
   `File → Open Config → [Your Config].zip`

Configurations can also be exported to `.zip` for easy sharing.

<br>

## Features

* Dynamic health and regeneration indicators
* Customizable colours, fonts, and display anchors
* Health threshold indicators with colour transitions
* Configurable skull icons for health state
* Ammo tracking with automatic colour calibration
* Optional static or dynamic crosshair
* Live configuration reloading when `Config/` files change
* Save and load configuration profiles as `.zip` files
* In-game ImGui configuration and testing interface

![App Screenshot](https://i.imgur.com/zsgPyPW.png)

---

## License

This project is provided as-is for personal and educational use.

All trademarks and game assets belong to their respective owners (Sea of Thieves © Microsoft / Rare Ltd).
