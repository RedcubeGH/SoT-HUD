import tkinter as tk
import win32gui
import win32con
import win32ui
import keyboard
from PIL import Image, ImageTk
import os
from ctypes import windll
import numpy as np

lowhealthvar = 70
lowhealthcolour = "#FF0000"
healthcolour = "#FFFF00"
numberhealthcolour = "#FFFFFF"
numberammocolour = "#FFFFFF"
crosshaircolour = "#FFFFFF"
crosshairoutlinecolour = "#080808"
font = "Arial"
ammosize = 25
hpsize = 25

script_dir = os.path.dirname(os.path.abspath(__file__))

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

# load shit
skullimg_path = os.path.join(script_dir, "Health_Bar_Skull.png")
fullskullimg = Image.open(skullimg_path)
scaledskullimg = fullskullimg.resize((38, 41), Image.NEAREST)
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

healthbar_path = os.path.join(script_dir, "Health_Bar_Decoration.png")
healthbar_img = Image.open(healthbar_path)
scaled_healthbar_img = healthbar_img.resize((320, 80), Image.NEAREST)
healthbar_arr = np.array(scaled_healthbar_img, dtype=np.uint16)
healthbar_arr[:, :, :3] += 2
np.clip(healthbar_arr, 0, 255, out=healthbar_arr)
healthbar_corrected = Image.fromarray(healthbar_arr.astype(np.uint8))
healthbarphoto = ImageTk.PhotoImage(healthbar_corrected)

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
    
# Create Crosshair
canvas.create_oval(
screen_width//2 - 2, screen_height//2 - 2,
screen_width//2 + 2, screen_height//2 + 2, 
fill=crosshaircolour, outline=crosshairoutlinecolour, tags="crosshair")

# keeps images in memory
canvas.ammogauge_photo = ammophoto
canvas.image = skullphoto

# Create Skull
canvas.create_image(140, 981, image=skullphoto, tags="skull_image")

#Create Healthbar
canvas.create_polygon(
170, 975,  # Top-left corner
183, 990,  # Bottom-left corner
393, 990,  # Bottom-right corner
380, 975,  # Top-right corner
outline="", tags="health")

# Create Healthbar Decoration
canvas.create_image(249, 982, image=healthbarphoto, tags="healthbardecoration")

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
        canvas.itemconfig("ammo", state="normal")
                    
        # Update Number Based Ammo and Crosshair
        if canvas.find_withtag("ammo"):
            canvas.itemconfig("numberammo", state="normal", text=f"{len(canvas.find_withtag("ammo"))}/5")
            canvas.itemconfig("crosshair", state="normal")
        else:
            canvas.itemconfig("numberammo", state="hidden")
            canvas.itemconfig("crosshair", state="hidden")
            
        #Update Healthbar
        pixel_colour = screen_img.getpixel((171, 975))
        hex_colour = '{:02X}{:02X}{:02X}'.format(*pixel_colour[:3])

        if hex_colour in {"3EDE7F", "ED3340", "3EDE7E", "EB3340"}:
            canvas.itemconfig("skull_image", state="normal")
            canvas.itemconfig("health", state="normal")
            canvas.itemconfig("numberhealth", state="normal")
            canvas.itemconfig("healthbardecoration", state="normal")
            
            # Update Health
            for hp in range(0, 100):
                pixel_colour = screen_img.getpixel((385-(2*hp), 984))
                hex_colour = '{:02X}{:02X}{:02X}'.format(*pixel_colour[:3])
                if hex_colour in {"43EF88", "FF3745", "43EF88", "FF3745"}:
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

                    break
        else:
            canvas.itemconfig("skull_image", state="hidden")
            canvas.itemconfig("health", state="hidden")
            canvas.itemconfig("numberhealth", state="hidden")  
            canvas.itemconfig("healthbardecoration", state="hidden")  

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
