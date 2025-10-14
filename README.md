# SoT-HUD
Author: Redcube

SoT HUD is a fully external Code of Conduct compliant HUD overlay for Sea of Thieves, built using PyQt5, glfw and ImGui for python version 3.11.
The program uses pixel scanning to update the overlay based on the in-game HUD which is then placed ontop of the pre-existing HUD.
The program doesn't interact with the Sea of Thieves Client at all except for Screen Capture and overlaying images on it which are both Code of Conduct compliant due to OBS and Crosshair X working the same.
Based on my interpretation of the Code of Conduct this software is safe to use without the risk of getting banned but Rare refuses to answer me with definite confirmation.


Installation

To run SoT HUD with python you'll need to install the following imports:
pip install pyqt5 glfw imgui[glfw] Pillow pywin32 keyboard
Or just clone the most recent release and execute the SoTHUD.exe file.
!!! Do not open SoT HUD while EAC is starting as it will cause the HUD to be very small!!!
SoT HUD is made for fullscreen so if you run Sea of Thieves in windowed mode it might not work as intended


Hotkeys

Press the delete key to close SoT HUD
Press the insert key to open the ImGui customization menu


Customization

The customization menu is pretty intuitive but if you require any help or want to check out other people's pre-made Configs be sure to join the paks discord discord.gg/swm3jwrN6M
To add other Configuration Profiles just download the .zip files given in the pak discord and put them in the YourConfigs Folder and then in ImGui just select your desired Config in the Toolbar under File>Open Config>[Your Config].zip


License

This project is provided as-is for personal and educational use.
All trademarks and game assets belong to their respective owners (Sea of Thieves © Microsoft / Rare Ltd).