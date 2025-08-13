import tkinter as tk
import win32gui
import win32con
import win32ui
import keyboard
from PIL import Image, ImageTk
import os
import time
from ctypes import windll
import numpy as np

lowhealthvar = 44
lowhealthcolour = "#FF0000"
healthcolour = "#00FF00"
numberhealthcolour = "#FFFFFF"
numberammocolour = "#FFFFFF"
font = "Arial"
ammosize = 25
hpsize = 25

script_dir = os.path.dirname(os.path.abspath(__file__))

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
fullskullimg = Image.open(skullimg_path)
scaledskullimg = fullskullimg.resize((40, 40), Image.NEAREST)
skullarr = np.array(scaledskullimg, dtype=np.uint16)
skullarr[:, :, :3] += 2
np.clip(skullarr, 0, 255, out=skullarr)
skullimg_corrected = Image.fromarray(skullarr.astype(np.uint8))
skullphoto = ImageTk.PhotoImage(skullimg_corrected)

ammogauge_path = os.path.join(script_dir, "ammogauge-pistol-ammunition.png")
ammogauge_img = Image.open(ammogauge_path)
scaled_ammogauge_img = ammogauge_img.resize((18, 17), Image.NEAREST)
ammogauge_arr = np.array(scaled_ammogauge_img, dtype=np.uint16)
ammogauge_arr[:, :, :3] += 2
np.clip(ammogauge_arr, 0, 255, out=ammogauge_arr)
ammogauge_corrected = Image.fromarray(ammogauge_arr.astype(np.uint8))
ammophoto = ImageTk.PhotoImage(ammogauge_corrected)

# keeps images in memory
canvas.ammogauge_photo = ammophoto
canvas.image = skullphoto

# Create Skull
canvas.create_image(141, 983, image=skullphoto, tags="skull_image")

#Create Healthbar
canvas.create_polygon(
170, 975,  # Top-left corner
183, 990,  # Bottom-left corner
393, 990,  # Bottom-right corner
380, 975,  # Top-right corner
outline="", tags="health"
)

# Number Based Health
canvas.create_text(217, 950, fill=numberhealthcolour, font=(font, hpsize), tags="numberhealth")

# Number Based Ammo
canvas.create_text(1680, 950, fill=numberammocolour, font=(font, ammosize), tags="numberammo")

def UpdateHUD():
    # only captures SoT
    hwnd = win32gui.FindWindow(None, 'Sea of Thieves')
    left, top, right, bot = win32gui.GetClientRect(hwnd)
    w = right - left
    h = bot - top

    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
    saveDC.SelectObject(saveBitMap)
    windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 2)

    
    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)

    screen_img = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1)    
    
    # Update Ammogauge
    for i in range(0, 6):
        pixel_colour = screen_img.getpixel((1642+(26*i), 980))
        hex_colour = '{:02X}{:02X}{:02X}'.format(*pixel_colour[:3])
        if hex_colour == "ADFFAB" and not canvas.find_withtag(f"ammo{i}"):  # check for ammo
            canvas.create_image(1642+(26*i), 980, image=ammophoto, tags=(f"ammo{i}", "ammo"))
        elif not hex_colour == "ADFFAB":
            canvas.delete(f"ammo{i}")
        else:
            break
        
    # Update Number Based Ammo
    if canvas.find_withtag("ammo"):
        canvas.itemconfig("numberammo", state="normal", text=f"{len(canvas.find_withtag("ammo"))}/5")
    else:
        canvas.itemconfig("numberammo", state="hidden")
     
    #Update Healthbar
    pixel_colour = screen_img.getpixel((171, 975))
    hex_colour = '{:02X}{:02X}{:02X}'.format(*pixel_colour[:3])
    
    if hex_colour in {"3EDE7F", "ED3340", "3EDE7E", "EB3340"}:
        canvas.itemconfig("skull_image", state="normal")
        canvas.itemconfig("health", state="normal")
        canvas.itemconfig("numberhealth", state="normal")
        
        # Update Health
        for hp in range(0, 100):
            pixel_colour = screen_img.getpixel((385-(2*hp), 984))
            hex_colour = '{:02X}{:02X}{:02X}'.format(*pixel_colour[:3])
            if hex_colour in {"43EF88", "FF3745", "43EF88", "FF3745"}:
                canvas.coords("health",
                168, 973,  # Top-left
                183, 989,  # Bottom-left
                398-(((398-190)/100)*hp), 989,  # Bottom-right
                383-(((383-176)/100)*hp), 973   # Top-right
                )
                if 100-hp <= lowhealthvar:
                    canvas.itemconfig("health", fill=lowhealthcolour)                
                else:
                    canvas.itemconfig("health", fill=healthcolour)
                canvas.itemconfig("numberhealth", text=f"{100-hp}/100")
    
                break
    else:
        canvas.itemconfig("skull_image", state="hidden")
        canvas.itemconfig("health", state="hidden")
        canvas.itemconfig("numberhealth", state="hidden")    
    
    # Cleanup
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)
    
    root.after(8, UpdateHUD) #loop every ms

UpdateHUD()
hwnd = win32gui.FindWindow(None, str(root.title()))
make_window_clickthrough(hwnd)
keyboard.add_hotkey('f3', lambda: root.destroy()) #killswitch
root.mainloop()
