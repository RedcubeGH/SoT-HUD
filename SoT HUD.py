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
from PIL import Image, ImageTk, ImageGrab

lowhealthvar = 70
lowhealthcolour = "#FF3700"
healthcolour = "#43EF88"
overhealcolour = "#FF0000"
numberhealthcolour = "#FFFFFF"
numberammocolour = "#FFFFFF"
crosshaircolour = "#FFFFFF"
crosshairoutlinecolour = "#080808"
font = "Arial"
ammosize = 25
hpsize = 25
ammotoggle = True
crosshairtoggle = True
healthbartoggle = True
healthbardecotoggle = True
skulltoggle = True
regentoggle = True
numberhealthtoggle = True
numberammotoggle = True
calibrated_ammo_colour = (173, 255, 171)
minregencolour = [0, 106, 0]
maxregencolour = [76, 239, 186]

script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "config.json")

root = tk.Tk()
root.attributes("-topmost", True)
root.attributes("-transparentcolor", "black")  # Transparent background
root.overrideredirect(True)  # Remove window border

# Make the window click-through
mainhwnd = win32gui.FindWindow(None, str(root.title()))
exStyle = win32gui.GetWindowLong(mainhwnd, win32con.GWL_EXSTYLE)
exStyle |= win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
    
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
        "numberhealthcolour": numberhealthcolour,
        "numberammocolour": numberammocolour,
        "crosshaircolour": crosshaircolour,
        "crosshairoutlinecolour": crosshairoutlinecolour,
        "font": font,
        "ammosize": ammosize,
        "hpsize": hpsize,
        "ammotoggle": ammotoggle,
        "crosshairtoggle": crosshairtoggle,
        "healthbartoggle": healthbartoggle,
        "healthbardecotoggle": healthbardecotoggle,
        "skulltoggle": skulltoggle,
        "regentoggle": regentoggle,
        "numberhealthtoggle": numberhealthtoggle,
        "numberammotoggle": numberammotoggle,
        "calibrated_ammo_colour": calibrated_ammo_colour
    }
    with open(config_path, "w") as f:
        json.dump(config_data, f)
    
# Check if ammo colour is calibrated
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
    while not screen_img.getpixel((1772, 980)) == screen_img.getpixel((1746, 980)) == screen_img.getpixel((1720, 980)) == screen_img.getpixel((1694, 980)) == screen_img.getpixel((1668, 980)):
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
        time.sleep(0.1)
    calibrated_ammo_colour = screen_img.getpixel((1772, 980))
    canvas.delete("calibration_text")
    save_config()

# load shit
green_skull_path = os.path.join(script_dir, "Health_Bar_Skull_Green.png")
green_skull_img = Image.open(green_skull_path)
scaled_green_skull_img = green_skull_img.resize((38, 41), Image.NEAREST)
green_skull_arr = np.array(scaled_green_skull_img, dtype=np.uint16)
green_skull_arr[:, :, :3] += 2
np.clip(green_skull_arr, 0, 255, out=green_skull_arr)
green_skull_corrected = Image.fromarray(green_skull_arr.astype(np.uint8))
green_skull_photo = ImageTk.PhotoImage(green_skull_corrected)

red_skull_path = os.path.join(script_dir, "Health_Bar_Skull_Red.png")
red_skull_img = Image.open(red_skull_path)
scaled_red_skull_img = red_skull_img.resize((38, 41), Image.NEAREST)
red_skull_arr = np.array(scaled_red_skull_img, dtype=np.uint16)
red_skull_arr[:, :, :3] += 2
np.clip(red_skull_arr, 0, 255, out=red_skull_arr)
red_skull_corrected = Image.fromarray(red_skull_arr.astype(np.uint8))
red_skull_photo = ImageTk.PhotoImage(red_skull_corrected)

ammogauge_path = os.path.join(script_dir, "ammogauge-pistol-ammunition.png")
ammogauge_img = Image.open(ammogauge_path)
scaled_ammogauge_img = ammogauge_img.resize((18, 17), Image.NEAREST)
ammogauge_arr = np.array(scaled_ammogauge_img, dtype=np.uint16)
ammogauge_arr[:, :, :3] += 2
np.clip(ammogauge_arr, 0, 255, out=ammogauge_arr)
ammogauge_corrected = Image.fromarray(ammogauge_arr.astype(np.uint8))
ammophoto = ImageTk.PhotoImage(ammogauge_corrected)

healthbar_frame_path = os.path.join(script_dir, "Health_Bar_BG_Frame.png")
healthbar_frame_img = Image.open(healthbar_frame_path)
scaled_healthbar_frame_img = healthbar_frame_img.resize((315, 100), Image.NEAREST)
healthbar_frame_arr = np.array(scaled_healthbar_frame_img, dtype=np.uint16)
healthbar_frame_arr[:, :, :3] += 2
np.clip(healthbar_frame_arr, 0, 255, out=healthbar_frame_arr)
healthbar_frame_corrected = Image.fromarray(healthbar_frame_arr.astype(np.uint8))
healthbar_frame_photo = ImageTk.PhotoImage(healthbar_frame_corrected)

regen_skull_path = os.path.join(script_dir, "Regen_Meter_Skull.png")
regen_skull_img = Image.open(regen_skull_path)
scaled_regen_skull_img = regen_skull_img.resize((60, 60), Image.NEAREST)
regen_skull_arr = np.array(scaled_regen_skull_img, dtype=np.uint16)
regen_skull_arr[:, :, :3] += 2
np.clip(regen_skull_arr, 0, 255, out=regen_skull_arr)
regen_skull_corrected = Image.fromarray(regen_skull_arr.astype(np.uint8))
regen_skull_photo = ImageTk.PhotoImage(regen_skull_corrected)

overlay_path = os.path.join(script_dir, "General_Overlay.png")
overlay_img = Image.open(overlay_path)
overlay_arr = np.array(overlay_img, dtype=np.uint16)
try:
    overlay_arr[:, :, :3] += 2
    np.clip(overlay_arr, 0, 255, out=overlay_arr)
    overlay_corrected = Image.fromarray(overlay_arr.astype(np.uint8))
    overlay_photo = ImageTk.PhotoImage(overlay_corrected)
    # Create General Overlay
    canvas.create_image(screen_width//2, screen_height//2, image=overlay_photo, tags="overlay")
except IndexError:
    print("Overlay image does not have an alpha channel, skipping Overlay")
    
# Create Regen Meter
canvas.create_oval(
115, 956,
165, 1007,
fill=overhealcolour, outline="", tags="regen_meter", state="hidden")
canvas.create_image(141, 982, image=regen_skull_photo, tags="regen_meter", state="hidden")

# Create Crosshair
canvas.create_oval(
screen_width//2 - 2.5, screen_height//2 - 2.5,
screen_width//2 + 2.5, screen_height//2 + 2.5, 
fill=crosshaircolour, outline=crosshairoutlinecolour, tags="crosshair")

# Create Ammo Gauge
for i in range(0, 6):
    canvas.create_image(1642+(26*i), 980, image=ammophoto, tags=(f"ammo{i}", "ammo"), state="hidden")

# Create Skull
canvas.create_image(140, 981, image=green_skull_photo, tags="green_skull_image", state="hidden")
canvas.create_image(140, 981, image=red_skull_photo, tags="red_skull_image", state="hidden")

#Create Healthbar
canvas.create_polygon(
170, 975,  # Top-left corner
183, 990,  # Bottom-left corner
393, 990,  # Bottom-right corner
380, 975,  # Top-right corner
outline="", tags="health")
canvas.create_image(256, 982, image=healthbar_frame_photo, tags="health_bar_bg")

# Number Based Health
canvas.create_text(217, 950, fill=numberhealthcolour, font=(font, hpsize), tags="numberhealth")

# Number Based Ammo
canvas.create_text(1680, 950, fill=numberammocolour, font=(font, ammosize), tags="numberammo")

def UpdateHUD():
    # only captures SoT
    hwnd = win32gui.FindWindow(None, 'Sea of Thieves')
    if hwnd == win32gui.GetForegroundWindow():
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
            
        #Update Healthbar
        pixel_colour = screen_img.getpixel((169, 977))
        control_colour = screen_img.getpixel((172, 976))

        if pixel_colour == screen_img.getpixel((141, 954)) == (0, 0, 0) != screen_img.getpixel((170, 977)):
                
            if numberhealthtoggle:
                canvas.itemconfig("numberhealth", state="normal")
                
            if healthbardecotoggle:
                canvas.itemconfig("health_bar_bg", state="normal")
                
            if regentoggle:
                # canvas.itemconfig("regen_meter", state="normal")
                for i in range(100):
                    theta = (2 * math.pi / 100) * i  # divide circle into 'steps' points
                    x = int(141 + 23 * math.cos(theta))
                    y = int(982 + 23 * math.sin(theta))
                    pixel_colour = screen_img.getpixel((x, y))
                    if pixel_colour[0] <= maxregencolour[0] and minregencolour[1] <= pixel_colour[1] <= maxregencolour[1] and pixel_colour[2] <= maxregencolour[2]:
                        print(f"Regen Pixel: {len(canvas.find_withtag('regen_meter'))}")
                        canvas.create_arc(
                            141 + 26, 982 + 26, 141 - 26, 982 - 26,
                            start=-i * (360 / 100),
                            extent=360 / 100,
                            style="pieslice",
                            outline="",
                            fill=overhealcolour,
                            tags="regen_meter", state="normal"
                        )
                    # debugging
                    # for i in range(3):
                    #     if pixel_colour[i] < minregencolour[i]:
                    #         minregencolour[i] = pixel_colour[i]
                            
                    #     if pixel_colour[i] > maxregencolour[i]:
                    #         maxregencolour[i] = pixel_colour[i]
                            
                    # print(f"min:{minregencolour} max:{maxregencolour}")
                    # canvas.create_rectangle(
                    #     x,y,x,y, fill="white", outline="")
                
            if healthbartoggle:
                canvas.itemconfig("health", state="normal")
                
                # Update Health
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
            canvas.itemconfig("red_skull_image", state="hidden")
            canvas.itemconfig("green_skull_image", state="hidden")
            canvas.itemconfig("health", state="hidden")
            canvas.itemconfig("numberhealth", state="hidden")  
            canvas.itemconfig("health_bar_bg", state="hidden")
            canvas.itemconfig("regen_meter", state="hidden")  

        # Cleanup
        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)
    else:
        canvas.itemconfig("all", state="hidden")
    # Make the window click-through  
    mainhwnd = win32gui.FindWindow(None, str(root.title()))
    win32gui.SetWindowLong(mainhwnd, win32con.GWL_EXSTYLE, exStyle)  
    root.after(8, UpdateHUD) #loop every ms

UpdateHUD()
keyboard.add_hotkey('f3', lambda: root.destroy()) #killswitch
root.mainloop()
