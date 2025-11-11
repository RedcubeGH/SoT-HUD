# Project: SoT HUD
# Author: Redcube

import os
import sys
import json
import math
from io import BytesIO
from PIL import Image
import win32gui
import win32con
import win32ui
from ctypes import windll
import keyboard
from PyQt5 import QtCore, QtGui, QtWidgets, QtCore
import glfw
import imgui
from imgui.integrations.glfw import GlfwRenderer
import threading
import time
from OpenGL.GL import *
import zipfile
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from windows_capture import WindowsCapture, Frame, InternalCaptureControl
import numpy as np

# Paths
script_dir  = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "..", "Config", "Config.json")

# defaults settings incase Config.json is missing or incomplete
class Config:
    # configurable variables
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
    ammotoggle              = True
    ammodecotoggle          = True
    crosshairtoggle         = False
    staticcrosshair         = False
    healthbartoggle         = True
    healthbardecotoggle     = True
    skulltoggle             = True
    regentoggle             = True
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

    # constants
    MINREGENCOLOUR          = [0, 88, 0]
    MAXREGENCOLOUR          = [76, 239, 186]
    
    # Non-config variables for imgui
    calibrated_ammo_colour  = (0, 0, 0)
    show_UI                 = False
    hp_slider               = 75.0
    regen_slider            = 50.0
    ammo_slider             = 5
    low_hp_slider           = lowhealthvar
    lowhealthvarchanged     = False
    healthoffset            = xoffsethealth, yoffsethealth
    ammooffset              = xoffsetammo, yoffsetammo
    regenoffset             = xoffsetregen, yoffsetregen
    Name                    = "My Config"
    popup                   = False
    current_font            = 0

    # load Config.json
    @classmethod
    def load_from_file(cls, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for k, v in data.items():
                if hasattr(cls, k):
                    setattr(cls, k, v)
        except Exception:
            pass
    
    calibrated_ammo_colour = tuple(calibrated_ammo_colour)

    if healthbardecotoggle and not regentoggle:
        regentoggle     = True
        overhealcolour  = "#4CEF7E"
        regenbgcolour   = "#676767"

    @classmethod
    def save_config(cls, export = False):
        cfg = {
            "lowhealthvar":             cls.lowhealthvar,
            "lowhealthcolour":          cls.lowhealthcolour,
            "healthcolour":             cls.healthcolour,
            "overhealcolour":           cls.overhealcolour,
            "regenbgcolour":            cls.regenbgcolour,
            "numberhealthcolour":       cls.numberhealthcolour,
            "numberammocolour":         cls.numberammocolour,
            "numberregencolour":        cls.numberregencolour,
            "crosshaircolour":          cls.crosshaircolour,
            "crosshairoutlinecolour":   cls.crosshairoutlinecolour,
            "font":                     cls.font,
            "ammosize":                 cls.ammosize,
            "hpsize":                   cls.hpsize,
            "regensize":                cls.regensize,
            "ammotoggle":               cls.ammotoggle,
            "ammodecotoggle":           cls.ammodecotoggle,
            "crosshairtoggle":          cls.crosshairtoggle,
            "staticcrosshair":          cls.staticcrosshair,
            "healthbartoggle":          cls.healthbartoggle,
            "healthbardecotoggle":      cls.healthbardecotoggle,
            "skulltoggle":              cls.skulltoggle,
            "regentoggle":              cls.regentoggle,
            "overlaytoggle":            cls.overlaytoggle,
            "numberhealthtoggle":       cls.numberhealthtoggle,
            "numberammotoggle":         cls.numberammotoggle,
            "numberregentoggle":        cls.numberregentoggle,
            "healthanchor":             cls.healthanchor,
            "xoffsethealth":            cls.xoffsethealth,
            "yoffsethealth":            cls.yoffsethealth,
            "ammoanchor":               cls.ammoanchor,
            "xoffsetammo":              cls.xoffsetammo,
            "yoffsetammo":              cls.yoffsetammo,
            "regenanchor":              cls.regenanchor,
            "xoffsetregen":             cls.xoffsetregen,
            "yoffsetregen":             cls.yoffsetregen,
            "healthprefix":             cls.healthprefix,
            "healthsuffix":             cls.healthsuffix,
            "ammoprefix":               cls.ammoprefix,
            "ammosuffix":               cls.ammosuffix,
            "regenprefix":              cls.regenprefix,
            "regensuffix":              cls.regensuffix,
            "calibrated_ammo_colour":   cls.calibrated_ammo_colour
        }
        if export:
            cfg.pop("calibrated_ammo_colour", None)
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=4)
        except Exception:
            pass
    
    @classmethod
    def load_config(cls, path):
        with zipfile.ZipFile(path, 'r') as zip_ref:
            zip_ref.extractall(os.path.join(script_dir, "..", "Config"))

def hex_to_rgb_f(hex_color):
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    return [r, g, b]

def rgb_f_to_hex(rgb):
    r, g, b = rgb
    return "#{:02X}{:02X}{:02X}".format(int(r*255), int(g*255), int(b*255))

def get_dyn_pos_right(pos):
    try:
        hwnd = win32gui.FindWindow(None, 'Sea of Thieves')
        return round(win32gui.GetClientRect(hwnd)[2]+get_dyn_x(pos-1920))
    except Exception:
        user32 = ctypes.windll.user32
        sot_width = user32.GetSystemMetrics(0)
        return round(sot_width+get_dyn_x(pos-1920))

def get_dyn_x(pos):
    try:
        hwnd = win32gui.FindWindow(None, 'Sea of Thieves')
        _, top, _, bot = win32gui.GetClientRect(hwnd)
        sot_height = bot - top
    except Exception:
        user32 = ctypes.windll.user32
        sot_height = user32.GetSystemMetrics(1)
    normal_sot_width = (sot_height / 9)*16
    return round((pos / 1920) * normal_sot_width)

def get_dyn_y(pos):
    try:
        hwnd = win32gui.FindWindow(None, 'Sea of Thieves')
        _, top, _, bot = win32gui.GetClientRect(hwnd)
        sot_height = bot - top
    except Exception:
        user32 = ctypes.windll.user32
        sot_height = user32.GetSystemMetrics(1)
    return round((pos / 1080) * sot_height)

# text anchor dict and function
ALIGN_MAP = {
    "n":        QtCore.Qt.AlignTop    | QtCore.Qt.AlignHCenter,
    "ne":       QtCore.Qt.AlignTop    | QtCore.Qt.AlignRight,
    "e":        QtCore.Qt.AlignRight  | QtCore.Qt.AlignVCenter,
    "se":       QtCore.Qt.AlignBottom | QtCore.Qt.AlignRight,
    "s":        QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter,
    "sw":       QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft,
    "w":        QtCore.Qt.AlignLeft   | QtCore.Qt.AlignVCenter,
    "nw":       QtCore.Qt.AlignTop    | QtCore.Qt.AlignLeft,
    "x":        QtCore.Qt.AlignCenter                       
}

def make_rect(x, y, xoffset, yoffset, anchor="x"):
    w = h = get_dyn_x(1920)
    half_w, half_h = w // 2, h // 2

    if anchor == "x":
        return QtCore.QRect((x + int(xoffset)) - half_w, (y + int(yoffset)) - half_h, w, h)

    elif anchor == "n":
        return QtCore.QRect((x + int(xoffset)) - half_w, (y + int(yoffset)), w, h)

    elif anchor == "ne":
        return QtCore.QRect((x + int(xoffset)) - w, (y + int(yoffset)), w, h)

    elif anchor == "e":
        return QtCore.QRect((x + int(xoffset)) - w, (y + int(yoffset)) - half_h, w, h)

    elif anchor == "se":
        return QtCore.QRect((x + int(xoffset)) - w, (y + int(yoffset)) - h, w, h)

    elif anchor == "s":
        return QtCore.QRect((x + int(xoffset)) - half_w, (y + int(yoffset)) - h, w, h)

    elif anchor == "sw":
        return QtCore.QRect((x + int(xoffset)), (y + int(yoffset)) - h, w, h)

    elif anchor == "w":
        return QtCore.QRect((x + int(xoffset)), (y + int(yoffset)) - half_h, w, h)

    elif anchor == "nw":
        return QtCore.QRect((x + int(xoffset)), (y + int(yoffset)), w, h)

TARGET_WINDOW = "Sea of Thieves"
latest_frame = None
frame_ready = False
# SoT capture
def start_capture():
    global capture
    
    capture = WindowsCapture(
        cursor_capture=False,
        draw_border=False,
        window_name=TARGET_WINDOW
    )

    @capture.event
    def on_frame_arrived(frame: Frame, capture_control: InternalCaptureControl):
        global latest_frame, frame_ready
        latest_frame = frame.frame_buffer[:, :, :3]  # BGRA → BGR
        frame_ready = True

    @capture.event
    def on_closed():
        print("Capture stopped")

    capture.start_free_threaded()
    
def get_pixel(x, y):
    global latest_frame, frame_ready
    if not frame_ready or latest_frame is None:
        return None
    try:
        b, g, r = latest_frame[y, x]
        return (r, g, b)  # return RGB
    except:
        return None
    
class PixmapManager:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.cache = {}

    def load(self, name, size=None):
        key = (name, size)
        path = os.path.join(self.base_dir, name)
        if not os.path.exists(path):
            return None
        img = Image.open(path).convert("RGBA")
        if size:
            img = img.resize(size, Image.LANCZOS)
        buf = BytesIO()
        img.save(buf, format="PNG")
        pix = QtGui.QPixmap()
        pix.loadFromData(buf.getvalue())
        self.cache[key] = pix
        return pix
    
class ConfigWatcher:
    def __init__(self, parent):
        self.parent = parent
        self.config_dir = os.path.join(os.path.dirname(__file__), "..", "Config")
        self.observer = None
        self._start()

    def _start(self):
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

        event_handler = _ConfigEventHandler(self.parent.update_config)
        self.observer = Observer()
        self.observer.schedule(event_handler, self.config_dir, recursive=True)
        self.observer.start()
        
    def stop(self):
        """Stops the watchdog observer thread cleanly."""
        if self.observer:
            self.observer.stop()
            self.observer.join()

class _ConfigEventHandler(FileSystemEventHandler):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def on_any_event(self, event):
        if not event.is_directory:
            self.callback()

class Overlay(QtWidgets.QWidget):
    # initializing the overlay
    def __init__(self, screen_width, screen_height):
        self.config_watcher = ConfigWatcher(self)
        flags = QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool
        super().__init__(None, flags)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowTransparentForInput)
        self.setGeometry(0, 0, screen_width, screen_height)

        # pixmaps passed from main
        self.load_all()

        # internal state
        self.fonts = QtGui.QFontDatabase().families()
        self.screen_img = None
        self.ammo_states = [False]*6
        self.numberammo_text = ""
        self.health_num_text = ""
        self.show_overlay = False
        self.regen_extent = 0
        self.regen_text = f"{Config.regenprefix}0{Config.regensuffix}"
        self.show_health = False
        self.show_regen = False
        self.show_skull_red = False
        self.show_skull_green = False
        self.current_hp = 0
        self.regen_extent = 0

        # calibration label
        self.calibration_label = QtWidgets.QLabel(self)
        self.calibration_label.setStyleSheet("color: white; font-size: 28px; background: rgba(0,0,0,160); padding: 8px;")
        self.calibration_label.setAlignment(QtCore.Qt.AlignCenter)
        self.calibration_label.setFixedWidth(1100)
        self.calibration_label.hide()

        # timer for loop
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_loop)
        self.timer.start(16)  # ~62.5 FPS

    # incase pyqt windowflag doesn't work js also do the shit that worked before (can't hurt can it)
    def set_click_through_native(self):
        try:
            hwnd = int(self.winId())
            exStyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            exStyle &= ~win32con.WS_EX_APPWINDOW
            exStyle &= ~win32con.WS_EX_TOOLWINDOW            
            exStyle |= win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, exStyle)
        except Exception as e:
            print("Failed to set native click-through:", e)
            
    def update_config(self):
        Config.load_from_file(config_path)
        time.sleep(0.1)
        self.load_all()
        self.update()

    def load_all(self):
        pm = PixmapManager(os.path.join(script_dir, "..", "Config"))
        self.green_skull_pix   = pm.load("Health_Bar_Skull_Green.png", (get_dyn_x(53),get_dyn_y(57)))
        self.red_skull_pix     = pm.load("Health_Bar_Skull_Red.png", (get_dyn_x(53), get_dyn_y(57)))
        self.ammo_bg_pix       = pm.load("ammogauge-BG-Frame.png", (get_dyn_x(352), get_dyn_y(126)))
        self.ammo_pix          = pm.load("ammogauge-pistol-ammunition.png", (get_dyn_x(22), get_dyn_y(22)))
        self.healthbar_bg_pix  = pm.load("Health_Bar_BG_Frame.png", (get_dyn_x(315), get_dyn_y(100)))
        self.regen_skull_pix   = pm.load("Regen_Meter_Skull.png", (get_dyn_x(60), get_dyn_y(60)))
        self.overlay_pix       = pm.load("General_Overlay.png", (get_dyn_x(1920), get_dyn_y(1080)))

    # this is the shit that handles the logic and instructs the painter what parts it should draw
    def update_loop(self):
        # calibration stage
        if Config.calibrated_ammo_colour == (0,0,0):
            self.calibration_label.setText("Pull out a gun with full ammo to calibrate ammo colour")
            self.calibration_label.move((self.screen_width - self.calibration_label.width())//2, self.screen_height - 140)
            self.calibration_label.show()
            QtWidgets.QApplication.processEvents()
            try:
                hwnd = win32gui.FindWindow(None, 'Sea of Thieves')
                if hwnd == 0:
                    raise RuntimeError("Game not found")
                #screen_img = capture_client(hwnd)
                px = get_pixel(get_dyn_pos_right(1772), get_dyn_y(980))
                cond = (px == get_pixel(get_dyn_pos_right(1746), get_dyn_y(980)) == get_pixel(get_dyn_pos_right(1720), get_dyn_y(980)) == get_pixel(get_dyn_pos_right(1694), get_dyn_y(980)) == get_pixel(get_dyn_pos_right(1668), get_dyn_y(980)) and (px[1] >= 178))
                if cond:
                    Config.calibrated_ammo_colour = tuple(int(x) for x in px)
                    self.calibration_label.hide()
                    Config.save_config(False)
                else:
                    # keep trying
                    pass
            except Exception as e:
                print(f"Couldn't calibrate ammo colour: {e}"+(" "*20), end="\r", flush=True)
            return

        try:
            # only do shit when game running and focused
            foreground = win32gui.GetForegroundWindow()
            hwnd = win32gui.FindWindow(None, 'Sea of Thieves')
            if hwnd and hwnd == foreground and not Config.show_UI:
                #self.screen_img = capture_client(hwnd)
                self.show_overlay = True

                # Ammo detection
                if Config.ammotoggle or Config.crosshairtoggle or Config.numberammotoggle:
                    for i in range(6):
                        px = get_pixel(get_dyn_pos_right(1642) + get_dyn_x(26*i), get_dyn_y(980))
                        if self.screen_height == 1440:
                            px = get_pixel(get_dyn_pos_right(1642) + 33*i, get_dyn_y(980))
                        if px == tuple(Config.calibrated_ammo_colour):
                            self.ammo_states[i] = True
                        else:
                            self.ammo_states[i] = False
                    if Config.numberammotoggle:
                        for i in range(6):
                            if self.ammo_states[i]:
                                ammocount = 6 - i
                                self.numberammo_text = f"{Config.ammoprefix}{ammocount}{Config.ammosuffix}"
                                break

                # Health/regen detection
                pixel_colour = get_pixel(get_dyn_x(169), get_dyn_y(977)) #supposed to be #000000
                control_colour = get_pixel(get_dyn_x(176), get_dyn_y(977)) #supposed to be colour of healthbar
                extra_px = get_pixel(get_dyn_x(141), get_dyn_y(955))
                # ensure all pixels were read successfully and use explicit comparisons to avoid ambiguous truth-value of arrays
                if (pixel_colour is not None and control_colour is not None and extra_px is not None and
                    max(pixel_colour[:3]) <= 3 and extra_px != control_colour and control_colour[1] >= 55 and not Config.show_UI):
                    # show hud pieces when healthbar is there
                    self.show_health = True
                    self.show_regen = True
                    regen_control_colour = get_pixel(get_dyn_x(141), get_dyn_y(958))
                    if (regen_control_colour[0] <= Config.MAXREGENCOLOUR[0] and
                        Config.MINREGENCOLOUR[1] <= regen_control_colour[1] <= Config.MAXREGENCOLOUR[1] and
                        regen_control_colour[2] <= Config.MAXREGENCOLOUR[2]):
                        for i in range(200):
                            theta = (2 * math.pi / 200) * -(i+50)
                            x = get_dyn_x(140 + 23 * math.cos(theta))
                            y = get_dyn_y(982 + 23 * math.sin(theta))
                            px = get_pixel(x, y)
                            if (px[0] <= Config.MAXREGENCOLOUR[0] and
                                Config.MINREGENCOLOUR[1] <= px[1] <= Config.MAXREGENCOLOUR[1] and
                                px[2] <= Config.MAXREGENCOLOUR[2]):
                                if Config.regentoggle:
                                    overhealhp = 360-((i)*1.8)
                                    self.regen_extent = int(overhealhp)
                                self.regen_text = f"{Config.regenprefix}{200-i}{Config.regensuffix}"
                                if i >= 198:
                                    self.regen_extent = 0
                                    self.regen_text = f"{Config.regenprefix}0{Config.regensuffix}"
                                break

                    for hp in range(100):
                        px = get_pixel(get_dyn_x(384 - (2*hp)), get_dyn_y(984))
                        if px == control_colour and px[1] >= 55:
                            self.current_hp = 100-hp
                            break

                    if Config.skulltoggle:
                        self.show_skull_red = (self.current_hp <= Config.lowhealthvar)
                        self.show_skull_green = not self.show_skull_red

                    if Config.numberhealthtoggle:
                        self.health_num_text = f"{Config.healthprefix}{self.current_hp}{Config.healthsuffix}"

                else:
                    # hide hud pieces if healthbar is not there
                    self.show_health = False
                    self.show_regen = False
                    self.health_num_text = ""
                    self.regen_text = f"{Config.regenprefix}0{Config.regensuffix}"
                    self.show_skull_red = False
                    self.show_skull_green = False
                    self.current_hp = 0
                    self.regen_extent = 0

                self.update()
            elif not Config.show_UI:
                # hide hud when game not focused or not running
                self.screen_img = None
                self.ammo_states = [False]*6
                self.numberammo_text = ""
                self.show_overlay = False
                self.show_health = False
                self.show_regen = False
                self.health_num_text = ""
                self.regen_text = f"{Config.regenprefix}0{Config.regensuffix}"
                self.show_skull_red = False
                self.show_skull_green = False
                self.current_hp = 0
                self.regen_extent = 0
                self.update()
            else:
                self.update()
        except Exception as e:
            print(f"{e} (Game is probably starting right now)"+("  "*20), end="\r", flush=True)

    # this is the shit that actually draws all of the HUD parts
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # overlay image
        if self.show_overlay and Config.overlaytoggle or Config.show_UI and Config.overlaytoggle:
            painter.drawPixmap((self.screen_width - self.overlay_pix.width()) // 2,
                               (self.screen_height - self.overlay_pix.height()) // 2,
                               self.overlay_pix)
        
        #ammo decoration
        if Config.ammodecotoggle and any(self.ammo_states) or Config.show_UI and Config.ammodecotoggle:
            painter.drawPixmap(get_dyn_pos_right(1546), get_dyn_y(919), self.ammo_bg_pix)
        
        # ammo image
        if Config.ammotoggle and any(self.ammo_states) or Config.show_UI and Config.ammotoggle:
            for i in range(6):
                x = get_dyn_pos_right(1642) + get_dyn_x(26*i)
                y = get_dyn_y(980)
                if self.screen_height == 1440:                      # insanely shitty temporary fix for the ammo being off on higher res (love sot jank)
                    x = get_dyn_pos_right(1648) + 33*i              # ammo spacing inconsistent and offset to the right by 6px for some reason
                    y = get_dyn_y(981)                              # offset down by 1px
                if self.screen_height == 2160:                      # 
                    x = get_dyn_pos_right(1641) + get_dyn_x(26*i)   # offset to the left by 1px
                    y = get_dyn_y(981)                              # offset down by 1px
                if self.ammo_states[i] and self.ammo_pix:
                    painter.drawPixmap(x - self.ammo_pix.width()//2, y - self.ammo_pix.height()//2, self.ammo_pix)
        
        # crosshair
        if Config.crosshairtoggle and (any(self.ammo_states) or Config.staticcrosshair) or Config.show_UI and Config.crosshairtoggle:
            painter.setBrush(QtGui.QColor(Config.crosshaircolour))
            painter.setPen(QtGui.QColor(Config.crosshairoutlinecolour))
            diameter = 4
            painter.drawEllipse(QtCore.QRectF(self.screen_width/2 - diameter/2, self.screen_height/2 - diameter/2, diameter, diameter))
            
        # healthbar polygon
        if Config.healthbartoggle and getattr(self, "current_hp", None) is not None and self.show_health or Config.show_UI and Config.healthbartoggle:
            hp = self.current_hp
            br_x = get_dyn_x(396 - (((396-192)/100)*(100-hp)))
            tr_x = get_dyn_x(380 - (((380-176)/100)*(100-hp)))
            pts = [QtCore.QPointF(get_dyn_x(165),get_dyn_y(973)), QtCore.QPointF(get_dyn_x(181),get_dyn_y(990)), QtCore.QPointF(br_x, get_dyn_y(990)), QtCore.QPointF(tr_x, get_dyn_y(973))]
            poly = QtGui.QPolygonF(pts)
            color = Config.lowhealthcolour if self.current_hp <= Config.lowhealthvar else Config.healthcolour
            painter.setBrush(QtGui.QColor(color))
            painter.setPen(QtCore.Qt.NoPen)
            painter.drawPolygon(poly)
        
        # low health line
        if Config.healthbartoggle and Config.lowhealthvarchanged and Config.show_UI:
            br_x = get_dyn_x(396 - (((396-192)/100)*(100-Config.lowhealthvar)))
            tr_x = get_dyn_x(380 - (((380-176)/100)*(100-Config.lowhealthvar)))
            pen = QtGui.QPen(QtCore.Qt.black, 4)
            painter.setPen(pen)
            painter.drawLine(br_x, get_dyn_y(990), tr_x, get_dyn_y(973))
            pen = QtGui.QPen(QtCore.Qt.red, 2)
            painter.setPen(pen)
            painter.drawLine(br_x, get_dyn_y(990), tr_x, get_dyn_y(973))

        # healthbar decoration
        if Config.healthbardecotoggle and self.healthbar_bg_pix and self.show_health or Config.show_UI and Config.healthbardecotoggle:
            painter.drawPixmap(get_dyn_x(256) - self.healthbar_bg_pix.width()//2, get_dyn_y(982) - self.healthbar_bg_pix.height()//2, self.healthbar_bg_pix)

        # regen meter background + arc + skull
        if Config.regentoggle and self.show_regen or Config.show_UI and Config.regentoggle:
            painter.setBrush(QtGui.QColor(Config.regenbgcolour))
            painter.setPen(QtCore.Qt.NoPen)
            painter.drawEllipse(QtCore.QRectF(get_dyn_x(114), get_dyn_y(954), get_dyn_x(54), get_dyn_y(54)))
            rect = QtCore.QRectF(get_dyn_x(141-27), get_dyn_y(981-27), get_dyn_x(55), get_dyn_y(55))
            start_deg = 90
            span_deg = -self.regen_extent
            start16 = int(start_deg * 16)
            span16 = int(span_deg * 16)
            painter.setBrush(QtGui.QColor(Config.overhealcolour))
            painter.drawPie(rect, start16, span16)
            if self.regen_skull_pix:
                painter.drawPixmap(get_dyn_x(141) - self.regen_skull_pix.width()//2, get_dyn_y(982) - self.regen_skull_pix.height()//2, self.regen_skull_pix)

        # skulls
        if Config.skulltoggle and self.show_health or Config.show_UI and Config.skulltoggle:
            if self.show_skull_green and self.green_skull_pix:
                painter.drawPixmap(get_dyn_x(140) - self.green_skull_pix.width()//2, get_dyn_y(981) - self.green_skull_pix.height()//2, self.green_skull_pix)
            if self.show_skull_red and self.red_skull_pix:
                painter.drawPixmap(get_dyn_x(140) - self.red_skull_pix.width()//2, get_dyn_y(981) - self.red_skull_pix.height()//2, self.red_skull_pix)
        
        # number health
        if Config.numberhealthtoggle and self.health_num_text and self.show_health or Config.show_UI and Config.numberhealthtoggle:
            painter.setPen(QtGui.QColor(Config.numberhealthcolour))
            font_q = QtGui.QFont(Config.font, Config.hpsize)
            painter.setFont(font_q)
            healthrect = make_rect(get_dyn_x(170), get_dyn_y(973), get_dyn_x(Config.xoffsethealth), get_dyn_y(Config.yoffsethealth), Config.healthanchor)
            painter.drawText(healthrect, ALIGN_MAP[Config.healthanchor], self.health_num_text)

        # number regen
        if Config.numberregentoggle and self.show_regen or Config.show_UI and Config.numberregentoggle:
            painter.setPen(QtGui.QColor(Config.numberregencolour))
            font_q = QtGui.QFont(Config.font, Config.regensize)
            painter.setFont(font_q)
            regenrect = make_rect(get_dyn_x(100), get_dyn_y(980), get_dyn_x(Config.xoffsetregen), get_dyn_y(Config.yoffsetregen), Config.regenanchor)
            painter.drawText(regenrect, ALIGN_MAP[Config.regenanchor], self.regen_text)
            
        # number ammo
        if Config.numberammotoggle and any(self.ammo_states) or Config.show_UI and Config.numberammotoggle:
            painter.setPen(QtGui.QColor(Config.numberammocolour))
            font_q = QtGui.QFont(Config.font, Config.ammosize)
            painter.setFont(font_q)
            ammorect = make_rect(get_dyn_pos_right(1620), get_dyn_y(980), get_dyn_x(Config.xoffsetammo), get_dyn_pos_right(Config.yoffsetammo), Config.ammoanchor)
            painter.drawText(ammorect, ALIGN_MAP[Config.ammoanchor], self.numberammo_text)
        painter.end()

def imgui_thread(overlay):
    anchor_grid = [
        ["nw", "n", "ne"],
        ["w", "x", "e"],
        ["sw", "s", "se"]
    ]
    
    if not glfw.init():
        print("Could not initialize GLFW")
        return

    # Create transparent window
    glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, glfw.TRUE)
    glfw.window_hint(glfw.RESIZABLE, glfw.FALSE)
    
    screen_width, screen_height = get_dyn_x(1904), get_dyn_y(1040)
    window = glfw.create_window(screen_width, screen_height, "SoT HUD UI", None, None)

    glfw.make_context_current(window)
    # Get current window style
    hwnd = glfw.get_win32_window(window)
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
    
    # Remove border styles but keep caption (toolbar)
    style &= ~win32con.WS_BORDER
    style &= ~win32con.WS_THICKFRAME
    style &= ~win32con.WS_DLGFRAME
    style &= ~win32con.WS_CAPTION

    # Apply new style
    win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
    glfw.swap_interval(1)
    
    exStyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)

    # remove taskbar icon (WS_EX_APPWINDOW) and add toolwindow flag (WS_EX_TOOLWINDOW)
    exStyle &= ~win32con.WS_EX_APPWINDOW
    exStyle |= win32con.WS_EX_TOOLWINDOW

    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, exStyle)

    win32gui.SetWindowPos(
        hwnd,
        win32con.HWND_TOPMOST,
        0, 0, 0, 0,
        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
    )
    def set_clickthrough(hwnd, enabled: bool):
        if enabled:
            exStyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            exStyle |= win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, exStyle)
        else:
            exStyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            exStyle &= ~win32con.WS_EX_TRANSPARENT
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, exStyle)
    
    # Create ImGui context and renderer
    imgui.create_context()
    impl = GlfwRenderer(window, attach_callbacks=True)
    
    while not glfw.window_should_close(window):
        glfw.poll_events()
        impl.process_inputs()
        
        # frame clear shit
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClear(GL_COLOR_BUFFER_BIT)
        impl.process_inputs()
        imgui.new_frame()
        if Config.show_UI:
            # All the healthbar customization options
            imgui.begin("SoT HUD config", flags=imgui.WINDOW_ALWAYS_AUTO_RESIZE |
                                            imgui.WINDOW_NO_SCROLLBAR|
                                            imgui.WINDOW_NO_COLLAPSE|
                                            imgui.WINDOW_MENU_BAR)
            if imgui.begin_menu_bar():
                if imgui.begin_menu('File'):
                    changed, _ = imgui.menu_item('Export config', None, False, True)
                    if changed:
                        Config.popup = True
                    with imgui.begin_menu('Open Config', True) as open_recent_menu:
                        if open_recent_menu.opened:
                            for file in os.listdir(os.path.join(script_dir, "..", "YourConfigs")):
                                changed, _ = imgui.menu_item(file, None, False, True)
                                if changed:
                                    Config.load_config(os.path.join(script_dir, "..", "YourConfigs", file))
                    imgui.end_menu()
                imgui.end_menu_bar()
            if Config.popup:
                imgui.open_popup("select-popup")
                Config.popup = False
            if imgui.begin_popup("select-popup"):
                imgui.text("Save config as:")
                _, Config.Name = imgui.input_text("##Name", Config.Name, 29)
                if imgui.button("Confirm"):
                    Config.save_config(True)
                    with zipfile.ZipFile(os.path.join(script_dir, "..", "YourConfigs", Config.Name+".zip"), 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                        for root, _, files in os.walk(os.path.join(script_dir, "..", "Config")):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, os.path.join(script_dir, "..", "Config"))
                                zip_ref.write(file_path, arcname)
                    imgui.close_current_popup()
                imgui.end_popup()    
            imgui.begin_tab_bar("MainTabBar")
            if imgui.begin_tab_item("Healthbar")[0]:
                changed, Config.healthbartoggle = imgui.checkbox("Healthbar", Config.healthbartoggle)
                if Config.healthbartoggle:
                    health_rgb = hex_to_rgb_f(Config.healthcolour)
                    changed, health_rgb = imgui.color_edit3("Health colour", *health_rgb)
                    if changed:
                        Config.healthcolour = rgb_f_to_hex(health_rgb)
                    changed, Config.low_hp_slider = imgui.slider_float("Critical health point", Config.low_hp_slider, 0, 100, "%.0f")
                    Config.lowhealthvar = int(Config.low_hp_slider)
                    if imgui.is_item_hovered() or imgui.is_item_active():
                        Config.lowhealthvarchanged = True
                    else:
                        Config.lowhealthvarchanged = False
                    lowhealth_rgb = hex_to_rgb_f(Config.lowhealthcolour)
                    changed, lowhealth_rgb = imgui.color_edit3("Low health colour", *lowhealth_rgb)
                    if changed:
                        Config.lowhealthcolour = rgb_f_to_hex(lowhealth_rgb)
                changed, Config.healthbardecotoggle = imgui.checkbox("Healthbar decorations", Config.healthbardecotoggle)
                if Config.healthbardecotoggle:
                    imgui.same_line()
                    if imgui.button("Open in Explorer"):
                        try:
                            file_to_select = os.path.normpath(os.path.join(script_dir, "..", "Config", "Health_Bar_BG_Frame.png"))
                            subprocess.run(["explorer", "/select,", file_to_select])
                        except Exception as e:
                            os.startfile(os.path.join(script_dir, "..", "Config"))
                        Config.show_UI = False
                changed, Config.numberhealthtoggle = imgui.checkbox("Health number", Config.numberhealthtoggle)
                if Config.numberhealthtoggle:
                    changed, Config.hpsize = imgui.drag_int("Font Size", Config.hpsize, 0.5, 1, 128)
                    changed, healthoffset = imgui.drag_int2("Position", Config.xoffsethealth, Config.yoffsethealth, 1, -screen_width, screen_width)
                    Config.xoffsethealth, Config.yoffsethealth = healthoffset
                    numberhealth_rgb = hex_to_rgb_f(Config.numberhealthcolour)
                    changed, numberhealth_rgb = imgui.color_edit3("", *numberhealth_rgb)
                    if changed:
                        Config.numberhealthcolour = rgb_f_to_hex(numberhealth_rgb)
                    for row_idx, row in enumerate(anchor_grid):
                        for col_idx, anchor in enumerate(row):
                            # Highlight the currently selected anchor
                            if anchor == Config.healthanchor:
                                imgui.push_style_color(imgui.COLOR_BUTTON, 0.3, 0.6, 0.9, 1.0)
                            else:
                                imgui.push_style_color(imgui.COLOR_BUTTON, 0.4, 0.4, 0.4, 1.0)
                            
                            # Draw the button
                            if imgui.button(anchor, width=25, height=25):
                                Config.healthanchor = anchor  # update selected anchor

                            imgui.pop_style_color()
                            if col_idx < len(row) - 1:
                                imgui.same_line()
                    imgui.columns(3, "health_columns", False)  # False disables borders
                    imgui.set_column_width(0, 90)
                    imgui.push_item_width(80)
                    changed, Config.healthprefix = imgui.input_text(" ", Config.healthprefix, 10)
                    imgui.next_column()
                    imgui.set_column_width(1, 30)
                    imgui.text(f"{int(Config.hp_slider)}")
                    imgui.next_column()
                    imgui.set_column_width(2, 136)
                    changed, Config.healthsuffix = imgui.input_text("  ", Config.healthsuffix, 11)
                    imgui.pop_item_width()
                    imgui.next_column()
                    imgui.columns(1)
                changed, Config.hp_slider = imgui.slider_float("Health testing slider", Config.hp_slider, 0, 100, "%.0f")
                imgui.end_tab_item()
                
            if imgui.begin_tab_item("Overheal")[0]:
                changed, Config.regentoggle = imgui.checkbox("Regen meter", Config.regentoggle)
                if Config.regentoggle:
                    overheal_rgb = hex_to_rgb_f(Config.overhealcolour)
                    changed, overheal_rgb = imgui.color_edit3("Overheal colour", *overheal_rgb)
                    if changed:
                        Config.overhealcolour = rgb_f_to_hex(overheal_rgb)
                    regenbg_rgb = hex_to_rgb_f(Config.regenbgcolour)
                    changed, regenbg_rgb = imgui.color_edit3("Background colour", *regenbg_rgb)
                    if changed:
                        Config.regenbgcolour = rgb_f_to_hex(regenbg_rgb)
                changed, Config.skulltoggle = imgui.checkbox("Healthbar skull", Config.skulltoggle)
                if Config.skulltoggle:
                    imgui.same_line()
                    if imgui.button("Open in Explorer"):
                        try:
                            file_to_select = os.path.normpath(os.path.join(script_dir, "..", "Config", "Health_Bar_Skull_Green.png"))
                            subprocess.run(["explorer", "/select,", file_to_select])
                        except Exception as e:
                            os.startfile(os.path.join(script_dir, "..", "Config"))
                        Config.show_UI = False
                changed, Config.numberregentoggle = imgui.checkbox("Overheal number", Config.numberregentoggle)
                if Config.numberregentoggle:
                    changed, Config.regensize = imgui.drag_int("Font Size", Config.regensize, 0.5, 1, 128)
                    changed, regenoffset = imgui.drag_int2("Position", Config.xoffsetregen, Config.yoffsetregen, 1, -screen_width, screen_width)
                    Config.xoffsetregen, Config.yoffsetregen = regenoffset
                    numberregen_rgb = hex_to_rgb_f(Config.numberregencolour)
                    changed, numberregen_rgb = imgui.color_edit3("", *numberregen_rgb)
                    if changed:
                        Config.numberregencolour = rgb_f_to_hex(numberregen_rgb)
                    for row_idx, row in enumerate(anchor_grid):
                        for col_idx, anchor in enumerate(row):
                            # Highlight the currently selected anchor
                            if anchor == Config.regenanchor:
                                imgui.push_style_color(imgui.COLOR_BUTTON, 0.3, 0.6, 0.9, 1.0)
                            else:
                                imgui.push_style_color(imgui.COLOR_BUTTON, 0.4, 0.4, 0.4, 1.0)
                            
                            # Draw the button
                            if imgui.button(anchor, width=25, height=25):
                                Config.regenanchor = anchor  # update selected anchor

                            imgui.pop_style_color()
                            if col_idx < len(row) - 1:
                                imgui.same_line()
                    imgui.columns(3, "regen_columns", False)  # False disables borders
                    imgui.set_column_width(0, 90)
                    imgui.push_item_width(80)
                    changed, Config.regenprefix = imgui.input_text(" ", Config.regenprefix, 10)
                    imgui.next_column()
                    imgui.set_column_width(1, 30)
                    imgui.text(f"{int(Config.regen_slider)}")
                    imgui.next_column()
                    imgui.set_column_width(2, 136)
                    changed, Config.regensuffix = imgui.input_text("  ", Config.regensuffix, 11)
                    imgui.pop_item_width()
                    imgui.next_column()
                    imgui.columns(1)
                changed, Config.regen_slider = imgui.slider_float("Regen testing slider", Config.regen_slider, 0, 200, "%.0f")
                imgui.end_tab_item()
            if imgui.begin_tab_item("Ammo")[0]:
                changed, Config.ammotoggle = imgui.checkbox("Ammo", Config.ammotoggle)
                if Config.ammotoggle:
                    imgui.same_line()
                    if imgui.button("Open in Explorer"):
                        try:
                            file_to_select = os.path.normpath(os.path.join(script_dir, "..", "Config", "ammogauge-pistol-ammunition.png"))
                            subprocess.run(["explorer", "/select,", file_to_select])
                        except Exception as e:
                            os.startfile(os.path.join(script_dir, "..", "Config"))
                        Config.show_UI = False
                changed, Config.ammodecotoggle = imgui.checkbox("Ammo decorations", Config.ammodecotoggle)
                if Config.ammodecotoggle:
                    imgui.same_line()
                    if imgui.button("Open in Explorer "):
                        try:
                            file_to_select = os.path.normpath(os.path.join(script_dir, "..", "Config", "ammogauge-BG-Frame.png"))
                            subprocess.run(["explorer", "/select,", file_to_select])
                        except Exception as e:
                            os.startfile(os.path.join(script_dir, "..", "Config"))
                        Config.show_UI = False
                changed, Config.numberammotoggle = imgui.checkbox("Ammo number", Config.numberammotoggle)
                if Config.numberammotoggle:
                    changed, Config.ammosize = imgui.drag_int("Font Size", Config.ammosize, 0.5, 1, 128)
                    changed, ammooffset = imgui.drag_int2("Position", Config.xoffsetammo, Config.yoffsetammo, 1, -screen_width, screen_width)
                    Config.xoffsetammo, Config.yoffsetammo = ammooffset
                    numberammo_rgb = hex_to_rgb_f(Config.numberammocolour)
                    changed, numberammo_rgb = imgui.color_edit3("", *numberammo_rgb)
                    if changed:
                        Config.numberammocolour = rgb_f_to_hex(numberammo_rgb)
                    for row_idx, row in enumerate(anchor_grid):
                        for col_idx, anchor in enumerate(row):
                            # Highlight the currently selected anchor
                            if anchor == Config.ammoanchor:
                                imgui.push_style_color(imgui.COLOR_BUTTON, 0.3, 0.6, 0.9, 1.0)
                            else:
                                imgui.push_style_color(imgui.COLOR_BUTTON, 0.4, 0.4, 0.4, 1.0)
                            
                            # Draw the button
                            if imgui.button(anchor, width=25, height=25):
                                Config.ammoanchor = anchor  # update selected anchor

                            imgui.pop_style_color()
                            if col_idx < len(row) - 1:
                                imgui.same_line()
                    imgui.columns(3, "ammo_columns", False)  # False disables borders
                    imgui.set_column_width(0, 90)
                    imgui.push_item_width(80)
                    changed, Config.ammoprefix = imgui.input_text(" ", Config.ammoprefix, 10)
                    imgui.next_column()
                    imgui.set_column_width(1, 30)
                    imgui.text(f"{int(Config.ammo_slider)}")
                    imgui.next_column()
                    imgui.set_column_width(2, 136)
                    changed, Config.ammosuffix = imgui.input_text("  ", Config.ammosuffix, 11)
                    imgui.pop_item_width()
                    imgui.next_column()
                    imgui.columns(1)
                changed, Config.ammo_slider = imgui.slider_int("Ammo testing slider", Config.ammo_slider, 0, 6, "%.0f")
                imgui.end_tab_item()
            if imgui.begin_tab_item("Misc")[0]:
                changed, Config.crosshairtoggle = imgui.checkbox("Crosshair", Config.crosshairtoggle)
                if Config.crosshairtoggle:
                    changed, Config.staticcrosshair = imgui.checkbox("Static crosshair", Config.staticcrosshair)
                    crosshair_rgb = hex_to_rgb_f(Config.crosshaircolour)
                    changed, crosshair_rgb = imgui.color_edit3("Crosshair colour", *crosshair_rgb)
                    if changed:
                        Config.crosshaircolour = rgb_f_to_hex(crosshair_rgb)
                    crosshairoutline_rgb = hex_to_rgb_f(Config.crosshairoutlinecolour)
                    changed, crosshairoutline_rgb = imgui.color_edit3("Crosshair outline colour", *crosshairoutline_rgb)
                    if changed:
                        Config.crosshairoutlinecolour = rgb_f_to_hex(crosshairoutline_rgb)
                changed, Config.overlaytoggle = imgui.checkbox("General overlay", Config.overlaytoggle)
                if Config.overlaytoggle:
                    imgui.same_line()
                    if imgui.button("Open in Explorer"):
                        try:
                            file_to_select = os.path.normpath(os.path.join(script_dir, "..", "Config", "General_Overlay.png"))
                            subprocess.run(["explorer", "/select,", file_to_select])
                        except Exception as e:
                            os.startfile(os.path.join(script_dir, "..", "Config"))
                        Config.show_UI = False
                try:
                    Config.current_font = overlay.fonts.index(Config.font)
                except ValueError:
                    Config.font = "MS Shell Dlg 2" # standard pyqt font if invalid font
                    Config.current_font = overlay.fonts.index(Config.font)
                clicked, Config.current_font = imgui.combo(
                    "Font", Config.current_font, overlay.fonts, 30)
                Config.font = overlay.fonts[Config.current_font]
                if imgui.button("Recalibrate ammo colour"):
                    Config.calibrated_ammo_colour = (0,0,0)
                imgui.end_tab_item()
            imgui.end_tab_bar()
            overlay.current_hp = Config.hp_slider
            if Config.hp_slider <= Config.lowhealthvar:
                overlay.show_skull_red = True
                overlay.show_skull_green = False
            else:
                overlay.show_skull_red = False
                overlay.show_skull_green = True
            overlay.health_num_text = f"{Config.healthprefix}{int(Config.hp_slider)}{Config.healthsuffix}"
            overlay.regen_extent = Config.regen_slider * 1.8
            overlay.regen_text = f"{Config.regenprefix}{int(Config.regen_slider)}{Config.regensuffix}"
            overlay.ammo_states = [False] * len(overlay.ammo_states)
            for i in range(5, 5 - Config.ammo_slider, -1):
                overlay.ammo_states[i] = True
            overlay.numberammo_text = f"{Config.ammoprefix}{Config.ammo_slider}{Config.ammosuffix}"
            imgui.end()

        # Render
        imgui.render()
        if Config.show_UI:
            set_clickthrough(hwnd, False)
        else:
            set_clickthrough(hwnd, True)
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)
        glfw.wait_events_timeout(0.01)

    impl.shutdown()
    glfw.terminate()

def main():    
    # create QApplication first
    app = QtWidgets.QApplication(sys.argv)
    start_capture()
    
    # query screen after creating app
    screen_geom = app.primaryScreen().geometry()
    screen_width = screen_geom.width()
    screen_height = screen_geom.height()

    # create and show overlay
    overlay = Overlay(screen_width, screen_height)
    overlay.show()

    # load config
    Config.load_from_file(config_path)
    
    # apply native click-through after show()
    overlay.set_click_through_native()
    
    # start imgui thread
    threading.Thread(target=imgui_thread, args=(overlay,), daemon=True).start()
    
    # keyboard hotkeys (global)
    keyboard.add_hotkey('delete', lambda: (print("Exiting..."+("      "*20)), Config.save_config(False), overlay.config_watcher.stop(), QtCore.QCoreApplication.quit()))
    keyboard.add_hotkey('insert', lambda: (setattr(Config, 'show_UI', not Config.show_UI), setattr(overlay, 'regen_extent', 0), setattr(overlay, 'regen_text', f"{Config.regenprefix}0{Config.regensuffix}")))
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()