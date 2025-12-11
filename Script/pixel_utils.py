# pixel_utils.py
import ctypes
import numpy as np
import win32gui
import win32ui
from ctypes import windll
from config import Config

def get_dyn_pos_right(pos):
    return round(Config.dynright+get_dyn_x(pos-1920))

def get_dyn_x(pos):
    normal_sot_width = (Config.sot_height / 9)*16
    return round((pos / 1920) * normal_sot_width)

def get_dyn_y(pos):
    return round((pos / 1080) * Config.sot_height)

def get_sizes():
    try:
        hwnd = win32gui.FindWindow(None, 'Sea of Thieves')
        _, dyntop, Config.dynright, dynbot = win32gui.GetClientRect(hwnd)
        Config.sot_height = dynbot - dyntop
    except:
        hwnd = win32gui.FindWindow(None, 'Sea of Thieves')
        user32 = ctypes.windll.user32
        Config.sot_height = user32.GetSystemMetrics(1)
        Config.dynright = Config.sot_width = user32.GetSystemMetrics(0)

def get_multiple_pixels(pixel_coords):
    if not pixel_coords:
        return []
    
    if Config.hwnd == 0:
        raise RuntimeError("Sea of Thieves window not found")
    
    left, top, right, bottom = win32gui.GetClientRect(Config.hwnd)
    width = right - left
    height = bottom - top
    
    # Prepare DCs once
    hwndDC = win32gui.GetWindowDC(Config.hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    
    # Create bitmap once
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(saveBitMap)
    
    # Single capture
    windll.user32.PrintWindow(Config.hwnd, saveDC.GetSafeHdc(), 3)
    
    # Extract entire image
    saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)
    img = np.frombuffer(bmpstr, dtype=np.uint8)
    img = img.reshape((height, width, 4))
    
    # Get all requested pixels
    pixels = []
    for x, y in pixel_coords:
        if 0 <= x < width and 0 <= y < height:
            pixel_rgb = img[y, x, :3][::-1]  # BGR → RGB
            pixels.append(pixel_rgb)
        else:
            pixels.append(None)
    
    # Cleanup
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(Config.hwnd, hwndDC)
    win32gui.DeleteObject(saveBitMap.GetHandle())
    
    return pixels