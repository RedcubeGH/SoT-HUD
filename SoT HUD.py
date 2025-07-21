import tkinter as tk
import win32gui
import win32con
import keyboard
from PIL import Image, ImageTk
import os
import time
from PIL import ImageGrab
script_dir = os.path.dirname(os.path.abspath(__file__))
ammocolour = "ADFFAB"

def make_window_clickthrough(hwnd):
    # Make the window click-through by changing its extended style (thx copilot :3)
    exStyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    exStyle |= win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, exStyle)

root = tk.Tk()
root.attributes("-topmost", True)
root.attributes("-transparentcolor", "black")  # Transparent background
root.overrideredirect(True)  # Remove window border

# fullscreen
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}+0+0")

canvas = tk.Canvas(root, width=screen_width, height=screen_height, bg="black", highlightthickness=0)
canvas.pack()

# load shit
skullimg_path = os.path.join(script_dir, "Health_Bar_Skull.png")
skullimg = Image.open(skullimg_path)
skullphoto = ImageTk.PhotoImage(skullimg)

ammogauge_path = os.path.join(script_dir, "ammogauge-pistol-ammunition.png")
ammogauge_img = Image.open(ammogauge_path)
ammophoto = ImageTk.PhotoImage(ammogauge_img)

# put shit in center
cx, cy = screen_width // 2, screen_height // 2

# canvas.create_polygon() ts prly for healthbar

def check_ammo():
    screen_img = ImageGrab.grab()
    for i in range(0, 6):
        pixel_colour = screen_img.getpixel((1642+(26*i), 980))
        hex_colour = '{:02X}{:02X}{:02X}'.format(*pixel_colour[:3])
        if hex_colour == ammocolour:  # check for ammo
            canvas.create_image(1642+(26*i), 980, image=ammophoto, tags="ammo")
            # stop shit from disappearing cus garbage
            canvas.ammogauge_photo = ammophoto
            canvas.create_rectangle(1642+(26*i), 980, 1642+(26*i), 980, fill="black", outline="", tags="ammo")
        else:
            canvas.delete("ammo")     

    pixel_colour = screen_img.getpixel((171, 975))
    hex_colour = '{:02X}{:02X}{:02X}'.format(*pixel_colour[:3])
    if not hex_colour == "3EDE7F" and not hex_colour == "ED3340":
        canvas.delete("skull_image")
    elif not canvas.find_withtag("skull_image"):
        canvas.create_image(cx, cy, image=skullphoto, tags="skull_image")
        # stop shit from disappearing cus garbage
        canvas.image = skullphoto
    else:
        pass
    root.after(1, check_ammo) #loop every ms

check_ammo()


hwnd = win32gui.FindWindow(None, str(root.title()))
make_window_clickthrough(hwnd)
keyboard.add_hotkey('f3', lambda: root.destroy()) #killswitch
root.mainloop()