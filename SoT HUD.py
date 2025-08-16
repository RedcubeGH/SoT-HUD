import win32gui
import win32con
import win32ui
import keyboard
import os
import json
import time
import math
import numpy as np
import tkinter as tk
from ctypes import windll
from PIL import Image, ImageTk

lowhealthvar = 70
lowhealthcolour = "#FF3700"
healthcolour = "#43EF88"
overhealcolour = "#43EF88"
regenbgcolour = "#353535"
numberhealthcolour = "#FFFFFF"
numberammocolour = "#FFFFFF"
numberregencolour = "#FFFFFF"
crosshaircolour = "#FFFFFF"
crosshairoutlinecolour = "#080808"
font = "Arial"
ammosize = 25
hpsize = 25
regensize = 25
ammotoggle = True
crosshairtoggle = True
healthbartoggle = True
healthbardecotoggle = True
skulltoggle = True
regentoggle = True
numberhealthtoggle = True
numberammotoggle = True
numberregentoggle = True
overlaytoggle = True
calibrated_ammo_colour = (173, 255, 171)
minregencolour = [0, 88, 0]
maxregencolour = [76, 239, 186]

script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "config.json")

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
        "numberhealthtoggle": numberhealthtoggle,
        "numberammotoggle": numberammotoggle,
        "numberregentoggle": numberregentoggle,
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
try:
    save_config()
except NameError:
    canvas.create_text(
        screen_width//2, screen_height//2,
        text="Pull out a gun with full ammo to calibrate ammo colour",
        fill="white", font=("Arial", 30), tags="calibration_text")
    root.update_idletasks()
    root.update()
    hwnd = win32gui.FindWindow(None, 'Sea of Thieves')
    screen_img = capture_client(hwnd)
    while not screen_img.getpixel((1772, 980)) == screen_img.getpixel((1746, 980)) == screen_img.getpixel((1720, 980)) == screen_img.getpixel((1694, 980)) == screen_img.getpixel((1668, 980)):
        hwnd = win32gui.FindWindow(None, 'Sea of Thieves')
        screen_img = capture_client(hwnd)
        time.sleep(0.1)
    calibrated_ammo_colour = screen_img.getpixel((1772, 980))
    canvas.delete("calibration_text")
    save_config()

# load shit
def load_image(filename, size=None):
    try:
        img = Image.open(os.path.join(script_dir, filename))
        if size:
            img = img.resize(size, Image.NEAREST)
        arr = np.array(img, dtype=np.uint16)
        arr[:, :, :3] += 2
        np.clip(arr, 0, 255, out=arr)
        return ImageTk.PhotoImage(Image.fromarray(arr.astype(np.uint8))), True
    except IndexError:
        print(f"{filename} does not have required RGB channels! Skipping {filename}")
        return None, False

green_skull_photo, skulltoggle              = load_image("Health_Bar_Skull_Green.png",      (38,41))
red_skull_photo, skulltoggle                = load_image("Health_Bar_Skull_Red.png",        (38, 41))
ammophoto, ammotoggle                       = load_image("ammogauge-pistol-ammunition.png", (18, 17))
healthbar_frame_photo, healthbardecotoggle  = load_image("Health_Bar_BG_Frame.png",         (315, 100))
regen_skull_photo, regentoggle              = load_image("Regen_Meter_Skull.png",           (60, 60))
overlay_photo, toggle=overlaytoggle         = load_image("General_Overlay.png")

# Create Overlay
if overlaytoggle:
    canvas.create_image(screen_width//2, screen_height//2, image=overlay_photo, tags="overlay")

# Create Regen Meter    
if regentoggle:
    canvas.create_oval(
    114, 954,
    168, 1007,
    fill=regenbgcolour, outline="", tags="regen_meter", state="hidden")
    arcid = canvas.create_arc(
        141 - 26, 982 - 26, 141 + 26, 982 + 26,
        start=88,
        style="pieslice",
        outline="",
        fill=overhealcolour,
        tags="regen_meter",
        state="hidden"
    )
    canvas.create_image(141, 982, image=regen_skull_photo, tags="regen_meter", state="hidden")

# Create Crosshair
if crosshairtoggle:
    canvas.create_oval(
    screen_width//2 - 2.5, screen_height//2 - 2.5,
    screen_width//2 + 2.5, screen_height//2 + 2.5, 
    fill=crosshaircolour, outline=crosshairoutlinecolour, tags="crosshair")

# Create Ammo Gauge
if ammotoggle:
    for i in range(0, 6):
        canvas.create_image(1642+(26*i), 980, image=ammophoto, tags=(f"ammo{i}", "ammo"), state="hidden")

# Create Skull
if skulltoggle:
    canvas.create_image(140, 981, image=green_skull_photo, tags="green_skull_image", state="hidden")
    canvas.create_image(140, 981, image=red_skull_photo, tags="red_skull_image", state="hidden")

# Create Healthbar
if healthbartoggle:
    canvas.create_polygon(
    170, 975,  # Top-left corner
    183, 990,  # Bottom-left corner
    393, 990,  # Bottom-right corner
    380, 975,  # Top-right corner
    outline="", tags="health")
if healthbardecotoggle:
    canvas.create_image(256, 982, image=healthbar_frame_photo, tags="health_bar_bg")

# Number Based Health
canvas.create_text(217, 950, fill=numberhealthcolour, font=(font, hpsize), tags="numberhealth")

# Number Based Ammo
canvas.create_text(1680, 950, fill=numberammocolour, font=(font, ammosize), tags="numberammo")

# Number Based Regen
canvas.create_text(140, 910, fill=numberregencolour, text="0/200", font=(font, regensize), tags="numberregen")

def UpdateHUD():
    hwnd = win32gui.FindWindow(None, 'Sea of Thieves')
    if hwnd == win32gui.GetForegroundWindow():
        screen_img = capture_client(hwnd)
        
        if overlaytoggle:
            canvas.itemconfig("overlay", state="normal")

        # Update Ammo and Crosshair
        if ammotoggle:
            for i in range(0, 6):
                pixel_colour = screen_img.getpixel((1642+(26*i), 980))
                if pixel_colour == calibrated_ammo_colour and canvas.itemcget(f"ammo{i}", "state") == "hidden":  # check for ammo
                    canvas.itemconfig(f"ammo{i}", state="normal")
                elif not pixel_colour == calibrated_ammo_colour:
                    canvas.itemconfig(f"ammo{i}", state="hidden")
                    canvas.itemconfig("numberammo", state="hidden")
                    canvas.itemconfig("crosshair", state="hidden")
                else:
                    if numberammotoggle:
                        ammocount = 6-i
                        canvas.itemconfig("numberammo", state="normal", text=f"{ammocount}/5")
                    if crosshairtoggle:
                        canvas.itemconfig("crosshair", state="normal")
                    break            
        
        # Update Healthbar
        pixel_colour = screen_img.getpixel((169, 977))
        control_colour = screen_img.getpixel((172, 976))

        if pixel_colour == screen_img.getpixel((141, 954)) == (0, 0, 0) != screen_img.getpixel((170, 977)):
                
            if numberhealthtoggle:
                canvas.itemconfig("numberhealth", state="normal")
                
            if healthbardecotoggle:
                canvas.itemconfig("health_bar_bg", state="normal")
                
            if numberregentoggle:
                canvas.itemconfig("numberregen", state="normal")
            
            # Update Overheal    
            if regentoggle:
                canvas.itemconfig("regen_meter", state="normal")
                for i in range(200):
                    theta = (2 * math.pi / 200) * -(i+50)
                    x = int(140 + 23 * math.cos(theta))
                    y = int(982 + 23 * math.sin(theta))
                    pixel_colour = screen_img.getpixel((x, y))
                    if pixel_colour[0] <= maxregencolour[0] and minregencolour[1] <= pixel_colour[1] <= maxregencolour[1] and pixel_colour[2] <= maxregencolour[2]:
                        overhealhp = 359.99-((i)*1.8)
                        canvas.itemconfig(arcid, extent = -(overhealhp))
                        canvas.itemconfig("numberregen", text=f"{200-i}/200")
                        break
                    if i == 199:
                        canvas.itemconfig(arcid, state="hidden")
                        canvas.itemconfig("numberregen", text="0/200")

                    # debugging
                    # for i in range(3):
                    #     if pixel_colour[i] < minregencolour[i]:
                    #         minregencolour[i] = pixel_colour[i]                            
                    #     if pixel_colour[i] > maxregencolour[i]:
                    #         maxregencolour[i] = pixel_colour[i]                            
                    # print(f"min:{minregencolour} max:{maxregencolour}")
                
            # Update Health
            if healthbartoggle:
                canvas.itemconfig("health", state="normal")
                for hp in range(100):
                    pixel_colour = screen_img.getpixel((385-(2*hp), 984))
                    if pixel_colour == control_colour and pixel_colour != (0, 0, 0):
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
                        canvas.itemconfig("numberhealth", text=f"{100-hp}/100")
                        
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
                "numberregen"
            ]:
                canvas.itemconfig(tag, state="hidden")
    else:
        canvas.itemconfig("all", state="hidden") 
    root.after(8, UpdateHUD) #loop at 125 FPS

UpdateHUD()
keyboard.add_hotkey('f3', lambda: root.destroy()) #killswitch
root.mainloop()
