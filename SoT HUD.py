# Project: SoT HUD
# Author: Redcube

import win32gui
import win32con
import win32ui
import keyboard
import os
import json
import time
import math
import webbrowser
import numpy as np
import tkinter as tk
from ctypes import windll
from PIL import Image, ImageTk

script_dir  = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "config.json")

lowhealthvar            = 70
lowhealthcolour         = "#FF3745"
healthcolour            = "#43EF88"
overhealcolour          = "#4CEF7E"
regenbgcolour           = "#676767"
numberhealthcolour      = "#FFFFFF"
numberammocolour        = "#FFFFFF"
numberregencolour       = "#FFFFFF"
crosshaircolour         = "#FFFFFF"
crosshairoutlinecolour  = "#080808"
font                    = "Times New Roman"
ammosize                = 25
hpsize                  = 25
regensize               = 25
ammotoggle              = False
crosshairtoggle         = False
healthbartoggle         = False
healthbardecotoggle     = False
skulltoggle             = False
regentoggle             = False
overlaytoggle           = False
numberhealthtoggle      = False
numberammotoggle        = False
numberregentoggle       = False
healthanchor            ="sw"
xoffsethealth           = 0
yoffsethealth           = 0
ammoanchor              ="e"
xoffsetammo             = 0
yoffsetammo             = 0
regenanchor             ="e"
xoffsetregen            = 0
yoffsetregen            = 0
healthprefix            = ""
healthsuffix            = "/100"
ammoprefix              = ""
ammosuffix              = "/5"   
regenprefix             = ""
regensuffix             = ""
calibrated_ammo_colour  = (0, 0, 0)

# constants for regen meter
minregencolour          = [0, 88, 0]
maxregencolour          = [76, 239, 186]
minammocolour           = [0, 178, 0]
maxhpcolour             = [173, 255, 207]

# Load configuration from config.json
with open(config_path, "r") as f:
    config_data = json.load(f)
    for key, value in config_data.items():
        if key in globals():
            globals()[key] = value
calibrated_ammo_colour = tuple(calibrated_ammo_colour)

root = tk.Tk()
root.attributes("-topmost", True)
root.attributes("-transparentcolor", "black")  # Transparent background
root.overrideredirect(True)  # Remove window border

# Make the window click-through
root.update()
mainhwnd = win32gui.FindWindow(None, str(root.title()))
exStyle = win32gui.GetWindowLong(mainhwnd, win32con.GWL_EXSTYLE)
exStyle |= win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
win32gui.SetWindowLong(mainhwnd, win32con.GWL_EXSTYLE, exStyle)
    
# fullscreen
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}+0+0")

canvas = tk.Canvas(root, width=screen_width, height=screen_height, bg="black", highlightthickness=0)
canvas.pack()

# Save the configuration
def save_config():
    config_data = {
        "lowhealthvar": lowhealthvar,
        "lowhealthcolour": lowhealthcolour,
        "healthcolour": healthcolour,
        "overhealcolour": overhealcolour,
        "regenbgcolour": regenbgcolour,
        "numberhealthcolour": numberhealthcolour,
        "numberammocolour": numberammocolour,
        "numberregencolour": numberregencolour,
        "crosshaircolour": crosshaircolour,
        "crosshairoutlinecolour": crosshairoutlinecolour,
        "font": font,
        "ammosize": ammosize,
        "hpsize": hpsize,
        "regensize": regensize,
        "ammotoggle": ammotoggle,
        "crosshairtoggle": crosshairtoggle,
        "healthbartoggle": healthbartoggle,
        "healthbardecotoggle": healthbardecotoggle,
        "skulltoggle": skulltoggle,
        "regentoggle": regentoggle,
        "overlaytoggle": overlaytoggle,
        "numberhealthtoggle": numberhealthtoggle,
        "numberammotoggle": numberammotoggle,
        "numberregentoggle": numberregentoggle,
        "healthanchor": healthanchor,
        "xoffsethealth": xoffsethealth,
        "yoffsethealth": yoffsethealth,
        "ammoanchor": ammoanchor,
        "xoffsetammo": xoffsetammo,
        "yoffsetammo": yoffsetammo,
        "regenanchor": regenanchor,
        "xoffsetregen": xoffsetregen,
        "yoffsetregen": yoffsetregen,
        "healthprefix": healthprefix,
        "healthsuffix": healthsuffix,
        "ammoprefix": ammoprefix,
        "ammosuffix": ammosuffix,
        "regenprefix": regenprefix,
        "regensuffix": regensuffix,
        "calibrated_ammo_colour": calibrated_ammo_colour
    }
    with open(config_path, "w") as f:
        json.dump(config_data, f, indent=4)

# only captures SoT
def capture_client(hwnd):
    left, top, right, bot = win32gui.GetClientRect(hwnd)
    w, h = right - left, bot - top
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
    saveDC.SelectObject(saveBitMap)
    windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 2)
    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)
    img = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
    win32gui.DeleteObject(saveBitMap.GetHandle()); saveDC.DeleteDC(); mfcDC.DeleteDC(); win32gui.ReleaseDC(hwnd, hwndDC)
    return img
    
# check if ammo colour is calibrated
if calibrated_ammo_colour == (0, 0, 0):
    while True:
        try:
            hwnd = win32gui.FindWindow(None, 'Sea of Thieves')
            screen_img = capture_client(hwnd)
            pixel_colour = screen_img.getpixel((1772, 980))
            canvas.create_text(
                screen_width//2, screen_height-100,
                text="Pull out a gun with full ammo to calibrate ammo colour",
                fill="white", font=("Arial", 30), tags="calibration_text")
            root.update_idletasks()
            root.update()
            while not screen_img.getpixel((1772, 980)) == screen_img.getpixel((1746, 980)) == screen_img.getpixel((1720, 980)) == screen_img.getpixel((1694, 980)) == screen_img.getpixel((1668, 980)) or pixel_colour[1] < 178:
                pixel_colour = screen_img.getpixel((1772, 980))
                hwnd = win32gui.FindWindow(None, 'Sea of Thieves')
                screen_img = capture_client(hwnd)
                time.sleep(0.1)
            calibrated_ammo_colour = screen_img.getpixel((1772, 980))
            canvas.delete("calibration_text")
            save_config()
            break
        except Exception as e:
            print(f" Game not found. Couldn't calibrate ammo colour: {e}" + ("    " * 10), end="\r", flush=True)
            time.sleep(0.5)

# load shit
def load_image(filename, size=None, toggle=True):
    try:
        img = Image.open(os.path.join(script_dir, filename))
        if size:
            img = img.resize(size, Image.NEAREST)
        arr = np.array(img, dtype=np.uint16)
        arr[:, :, :3] += 2
        np.clip(arr, 0, 255, out=arr)
        return ImageTk.PhotoImage(Image.fromarray(arr.astype(np.uint8))), toggle
    except IndexError:
        print(f"{filename} does not have required RGB channels! Skipping {filename}")
        return None, False

green_skull_photo, skulltoggle              = load_image("Health_Bar_Skull_Green.png",      (53,57), skulltoggle)
red_skull_photo, skulltoggle                = load_image("Health_Bar_Skull_Red.png",        (53,57), skulltoggle)
ammophoto, ammotoggle                       = load_image("ammogauge-pistol-ammunition.png", (18,17), ammotoggle)
healthbar_frame_photo, healthbardecotoggle  = load_image("Health_Bar_BG_Frame.png",         (315,100), healthbardecotoggle)
regen_skull_photo, regentoggle              = load_image("Regen_Meter_Skull.png",           (60,60), regentoggle)
overlay_photo, overlaytoggle                = load_image("General_Overlay.png",             toggle=overlaytoggle)

# Create Overlay
if overlaytoggle:
    print("Overlay initialized")
    canvas.create_image(screen_width//2, screen_height//2, image=overlay_photo, tags="overlay")

# Create Regen Meter   
canvas.create_oval(
114, 954,
168, 1007,
fill=regenbgcolour, outline="", tags="regen_meter", state="hidden")
arcid = canvas.create_arc(
    141 - 26, 981 - 26, 141 + 26, 982 + 26,
    start=88,
    extent = 0,
    style="pieslice",
    outline="",
    fill=overhealcolour,
    state="hidden") 
if regentoggle:
    print("Regen Meter initialized")
    canvas.create_image(141, 982, image=regen_skull_photo, tags="regen_meter", state="hidden")

# Create Crosshair
if crosshairtoggle:
    print("Crosshair initialized")
    canvas.create_oval(
    screen_width//2 - 2.5, screen_height//2 - 2.5,
    screen_width//2 + 2.5, screen_height//2 + 2.5, 
    fill=crosshaircolour, outline=crosshairoutlinecolour, tags="crosshair")

# Create Ammo Gauge
if ammotoggle:
    print("Ammo Gauge initialized")
    for i in range(0, 6):
        canvas.create_image(1642+(26*i), 980, image=ammophoto, tags=(f"ammo{i}", "ammo"), state="hidden")

# Create Skull
if skulltoggle:
    print("Skull initialized")
    canvas.create_image(140, 981, image=green_skull_photo, tags="green_skull_image", state="hidden")
    canvas.create_image(140, 981, image=red_skull_photo, tags="red_skull_image", state="hidden")

# Create Healthbar
if healthbartoggle:
    print("Healthbar initialized")
    canvas.create_polygon(
    170, 975,  # Top-left corner
    183, 990,  # Bottom-left corner
    393, 990,  # Bottom-right corner
    380, 975,  # Top-right corner
    outline="", tags="health")
if healthbardecotoggle:
    print("Healthbar Decoration initialized")
    canvas.create_image(256, 982, image=healthbar_frame_photo, tags="health_bar_bg")

# Number Based Health
if numberhealthtoggle:
    print("Number Based Health initialized")
    canvas.create_text(170 + xoffsethealth, 973 + yoffsethealth, fill=numberhealthcolour, font=(font, hpsize), anchor=healthanchor, tags="numberhealth")

# Number Based Ammo
if numberammotoggle:
    print("Number Based Ammo initialized")
    canvas.create_text(1620 + xoffsetammo, 980 + yoffsetammo, fill=numberammocolour, font=(font, ammosize), anchor=ammoanchor, tags="numberammo")

# Number Based Regen
if numberregentoggle:
    print("Number Based Regen initialized")
    canvas.create_text(100 + xoffsetregen, 980 + yoffsetregen, fill=numberregencolour, text=f"{regenprefix}0{regensuffix}", font=(font, regensize), tags="numberregen", anchor=regenanchor, state="hidden")

print(" Game not running or not in focus" + ("    " * 20), end="\r", flush=True)

def UpdateHUD():
    hwnd = win32gui.FindWindow(None, 'Sea of Thieves')
    if hwnd == win32gui.GetForegroundWindow():
        try:
            print(" Game found updating HUD" + ("    " * 20), end="\r", flush=True)
            
            screen_img = capture_client(hwnd)
            
            if overlaytoggle:
                canvas.itemconfig("overlay", state="normal")
            
            # Update Ammo and Crosshair
            if ammotoggle or crosshairtoggle or numberammotoggle:
                for i in range(0, 6):
                    pixel_colour = screen_img.getpixel((1642+(26*i), 980))
                    if pixel_colour == calibrated_ammo_colour and canvas.itemcget(f"ammo{i}", "state") == "hidden":  # check for ammo
                        if ammotoggle:
                            canvas.itemconfig(f"ammo{i}", state="normal")
                    elif not pixel_colour == calibrated_ammo_colour:
                        canvas.itemconfig(f"ammo{i}", state="hidden")
                        canvas.itemconfig("numberammo", state="hidden")
                        canvas.itemconfig("crosshair", state="hidden")
                    else:
                        if numberammotoggle:
                            ammocount = 6-i
                            canvas.itemconfig("numberammo", state="normal", text=f"{ammoprefix}{ammocount}{ammosuffix}")
                        if crosshairtoggle:
                            canvas.itemconfig("crosshair", state="normal")
                        break
            
            # Update Healthbar
            pixel_colour = screen_img.getpixel((169, 977))
            control_colour = screen_img.getpixel((172, 976))
            bar_colour = screen_img.getpixel((172, 976))
            
            if pixel_colour == screen_img.getpixel((141, 954)) == (0, 0, 0) != bar_colour and bar_colour[1] >= 55:
                        
                if numberhealthtoggle:
                    canvas.itemconfig("numberhealth", state="normal")
                    
                if healthbardecotoggle:
                    canvas.itemconfig("health_bar_bg", state="normal")
                    
                if numberregentoggle:
                    canvas.itemconfig("numberregen", state="normal")
                    
                if healthbartoggle:
                    canvas.itemconfig("health", state="normal")
                
                if regentoggle or numberregentoggle:
                    canvas.itemconfig("regen_meter", state="normal")
                    regen_control_colour = screen_img.getpixel((141, 958))
                    if regen_control_colour[0] <= maxregencolour[0] and minregencolour[1] <= regen_control_colour[1] <= maxregencolour[1] and regen_control_colour[2] <= maxregencolour[2]:
                        for i in range(200):
                            theta = (2 * math.pi / 200) * -(i+50)
                            x = int(140 + 23 * math.cos(theta))
                            y = int(982 + 23 * math.sin(theta))
                            pixel_colour = screen_img.getpixel((x, y))
                            if pixel_colour[0] <= maxregencolour[0] and minregencolour[1] <= pixel_colour[1] <= maxregencolour[1] and pixel_colour[2] <= maxregencolour[2]:
                                if regentoggle:
                                    overhealhp = 359.99-((i)*1.8)
                                    canvas.itemconfig(arcid, extent = -(overhealhp), state="normal")
                                canvas.itemconfig("numberregen", text=f"{regenprefix}{200-i}{regensuffix}")
                                if i >= 198:
                                    canvas.itemconfig(arcid, state="hidden")
                                    canvas.itemconfig("numberregen", text=f"{regenprefix}0{regensuffix}")
                                break
                    
                # Update Health
                for hp in range(100):
                    pixel_colour = screen_img.getpixel((385-(2*hp), 984))
                    if pixel_colour == control_colour and pixel_colour[1] >= 55:
                        if healthbartoggle:
                            canvas.coords("health",
                            167, 974,  # Top-left
                            182, 989,  # Bottom-left
                            395-(((395-191)/100)*hp), 990,  # Bottom-right
                            380-(((380-176)/100)*hp), 974   # Top-right
                            )
                            if 100-hp <= lowhealthvar:
                                canvas.itemconfig("health", fill=lowhealthcolour)                
                            else:
                                canvas.itemconfig("health", fill=healthcolour)
                        canvas.itemconfig("numberhealth", text=f"{healthprefix}{100-hp}{healthsuffix}")
                        
                        if skulltoggle:
                            if 100-hp <= lowhealthvar:
                                canvas.itemconfig("red_skull_image", state="normal")
                                canvas.itemconfig("green_skull_image", state="hidden")
                            else:
                                canvas.itemconfig("red_skull_image", state="hidden")
                                canvas.itemconfig("green_skull_image", state="normal")
                        break
            else:
                for tag in [
                    "red_skull_image",
                    "green_skull_image",
                    "health",
                    "numberhealth",
                    "health_bar_bg",
                    "regen_meter",
                    "numberregen",
                    arcid
                ]:
                    canvas.itemconfig(tag, state="hidden")
                canvas.itemconfig("numberregen", text=f"{regenprefix}0{regensuffix}")
        except Exception as e:
            print(f" Error capturing screen: {e} (Game is probably starting right now)" + ("    " * 20), end="\r", flush=True)
    else:
        canvas.itemconfig("all", state="hidden") 
    root.after(16, UpdateHUD) #loop at 125 FPS

UpdateHUD()
keyboard.add_hotkey('f3', lambda: root.destroy()) #killswitch
keyboard.add_hotkey("insert", lambda: webbrowser.open("http://localhost:3000"))
root.mainloop()





