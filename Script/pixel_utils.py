# pixel_utils.py
import ctypes
import numpy as np
import win32gui
import win32ui
from ctypes import windll

# runtime globals
hwnd = 0
dynright = 0
sot_height = 1080
sot_width = 1920

def get_dyn_pos_right(pos):
    try:
        return round(dynright + get_dyn_x(pos - 1920))
    except Exception:
        return round(sot_width + get_dyn_x(pos - 1920))

def get_dyn_x(pos):
    try:
        normal_sot_width = (sot_height / 9) * 16
        return round((pos / 1920) * normal_sot_width)
    except Exception:
        return round((pos / 1920) * 1920)

def get_dyn_y(pos):
    return round((pos / 1080) * sot_height)

def get_sizes():
    # Updates module-level hwnd, dynright, sot_height and sot_width
    global hwnd, dynright, sot_height, sot_width
    try:
        hwnd = win32gui.FindWindow(None, 'Sea of Thieves')
        _, dyntop, dynright, dynbot = win32gui.GetClientRect(hwnd)
        sot_height = dynbot - dyntop
        # approximate width
        sot_width = round((sot_height / 9) * 16)
    except Exception:
        user32 = ctypes.windll.user32
        sot_height = user32.GetSystemMetrics(1)
        sot_width = user32.GetSystemMetrics(0)
        hwnd = 0

def get_multiple_pixels(pixel_coords):
    global hwnd
    if not pixel_coords:
        return []
    if hwnd == 0:
        raise RuntimeError("Sea of Thieves window not found")
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    width = right - left
    height = bottom - top

    # Device contexts
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    # Bitmap
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(saveBitMap)

    # Capture
    windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 3)

    # Extract image bytes
    bmpstr = saveBitMap.GetBitmapBits(True)
    img = np.frombuffer(bmpstr, dtype=np.uint8)
    try:
        img = img.reshape((height, width, 4))
    except Exception:
        # fallback if shape mismatch
        img = img.copy()
        img = img.reshape((height, width, 4))

    pixels = []
    for x, y in pixel_coords:
        if 0 <= x < width and 0 <= y < height:
            pixel_rgb = img[y, x, :3][::-1]  # BGR -> RGB
            pixels.append(pixel_rgb)
        else:
            pixels.append(None)

    # cleanup
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)
    win32gui.DeleteObject(saveBitMap.GetHandle())

    return pixels