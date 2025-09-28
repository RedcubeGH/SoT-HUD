# Project: SoT HUD
# Author: Redcube

import os
import sys
import json
import math
import webbrowser
from io import BytesIO
from PIL import Image
import win32gui
import win32con
import win32ui
from ctypes import windll
import keyboard
from PyQt5 import QtCore, QtGui, QtWidgets, QtCore
import glfw
import OpenGL.GL as gl
import imgui
from imgui.integrations.glfw import GlfwRenderer
import threading
import time
from OpenGL.GL import *
from fontTools.ttLib import TTFont

# Paths
script_dir  = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "config.json")

# defaults settings incase config.json is missing or incomplete
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
minregencolour          = [0, 88, 0]
maxregencolour          = [76, 239, 186]
minammocolour           = [0, 178, 0]
maxhpcolour             = [173, 255, 207]
calibrated_ammo_colour  = (0, 0, 0)
show_UI                 = False
hp_slider               = 75.0
regen_slider            = 50.0
ammo_slider             = 5
low_hp_slider           = lowhealthvar
lowhealthvarchanged     = False
current_font            = 0
font_dir                = "C:\Windows\Fonts"
font_files              = [os.path.join(font_dir, f) for f in os.listdir(font_dir) if f.lower().endswith((".ttf", ".otf"))]
healthoffset            = xoffsethealth, yoffsethealth
ammooffset              = xoffsetammo, yoffsetammo
regenoffset             = xoffsetregen, yoffsetregen

def get_font_title(font_path: str) -> str:
    font = TTFont(font_path, fontNumber=0)
    name = font['name']
    # NameID 4 = Full Font Name
    for record in name.names:
        if record.nameID == 4:
            return str(record.string, record.getEncoding()).strip()


fonts = [get_font_title(f) for f in font_files]
if not fonts:
    fonts = ["No fonts found"]

# load config.json
try:
    with open(config_path, "r", encoding="utf-8") as f:
        config_data = json.load(f)
        for key, value in config_data.items():
            if key in globals():
                globals()[key] = value
except Exception as e:
    pass
calibrated_ammo_colour = tuple(calibrated_ammo_colour)

if healthbardecotoggle and not regentoggle:
    regentoggle     = True
    overhealcolour  = "#4CEF7E"
    regenbgcolour   = "#676767"

def save_config():
    cfg = {
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
        "ammodecotoggle": ammodecotoggle,
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
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4)
    except Exception:
        pass

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
    "x":   QtCore.Qt.AlignCenter,                       
}

def make_rect(x, y, xoffset, yoffset, anchor="x"):
    w = h = 500
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

# SoT capture
def capture_client(hwnd):
    left, top, right, bot = win32gui.GetClientRect(hwnd)
    w, h = right - left, bot - top
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
    saveDC.SelectObject(saveBitMap)
    windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 3)
    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)
    img = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
    # cleanup
    win32gui.DeleteObject(saveBitMap.GetHandle()); saveDC.DeleteDC(); mfcDC.DeleteDC(); win32gui.ReleaseDC(hwnd, hwndDC)
    return img

# load shit as qpixmap
def load_pixmap_bytes(filename, size=None):
    path = os.path.join(script_dir, filename)
    if not os.path.exists(path):
        return None
    img = Image.open(path).convert("RGBA")
    if size:
        img = img.resize(size, Image.LANCZOS)
    buf = BytesIO()
    img.save(buf, format="PNG")
    data = buf.getvalue()
    pix = QtGui.QPixmap()
    pix.loadFromData(data)
    return pix

class Overlay(QtWidgets.QWidget):
    # initializing the overlay
    def __init__(self, screen_width, screen_height, pixmaps):
        flags = QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool
        super().__init__(None, flags)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowTransparentForInput)

        self.setGeometry(0, 0, screen_width, screen_height)

        # pixmaps passed from main
        (self.green_skull_pix,
         self.red_skull_pix,
         self.ammo_bg_pix,
         self.ammo_pix,
         self.healthbar_bg_pix,
         self.regen_skull_pix,
         self.overlay_pix) = pixmaps

        # internal state
        self.screen_img = None
        self.calibrated_ammo_colour = calibrated_ammo_colour
        self.ammo_states = [False]*6
        self.numberammo_text = ""
        self.health_num_text = ""
        self.show_overlay = False
        self.regen_extent = 0
        self.regen_text = f"{regenprefix}0{regensuffix}"
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
            exStyle |= win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, exStyle)
        except Exception as e:
            print("Failed to set native click-through:", e)

    # this is the shit that handles the logic and instructs the painter what parts it should draw
    def update_loop(self):
        # calibration stage
        if self.calibrated_ammo_colour == (0,0,0):
            self.calibration_label.setText("Pull out a gun with full ammo to calibrate ammo colour")
            self.calibration_label.move((self.screen_width - self.calibration_label.width())//2, self.screen_height - 140)
            self.calibration_label.show()
            QtWidgets.QApplication.processEvents()
            try:
                hwnd = win32gui.FindWindow(None, 'Sea of Thieves')
                if hwnd == 0:
                    raise RuntimeError("Game not found")
                screen_img = capture_client(hwnd)
                px = screen_img.getpixel((get_dyn_pos_right(1772), get_dyn_y(980)))
                cond = (px == screen_img.getpixel((get_dyn_pos_right(1746), get_dyn_y(980))) == screen_img.getpixel((get_dyn_pos_right(1720), get_dyn_y(980))) == screen_img.getpixel((get_dyn_pos_right(1694), get_dyn_y(980))) == screen_img.getpixel((get_dyn_pos_right(1668), get_dyn_y(980)))) and (px[1] >= 178)
                if cond:
                    self.calibrated_ammo_colour = px
                    global calibrated_ammo_colour
                    calibrated_ammo_colour = tuple(px)
                    save_config()
                    self.calibration_label.hide()
                else:
                    # keep trying
                    pass
            except Exception as e:
                print(f" Game not found. Couldn't calibrate ammo colour: {e}"+(" "*20), end="\r", flush=True)
            return

        try:
            # only do shit when game running and focused
            foreground = win32gui.GetForegroundWindow()
            hwnd = win32gui.FindWindow(None, 'Sea of Thieves')
            if hwnd and hwnd == foreground and not show_UI:
                self.screen_img = capture_client(hwnd)
                self.show_overlay = True

                # Ammo detection
                if ammotoggle or crosshairtoggle or numberammotoggle:
                    for i in range(6):
                        px = self.screen_img.getpixel((get_dyn_pos_right(1642) + get_dyn_x(26*i), get_dyn_y(980)))
                        if self.screen_height == 1440:
                            px = self.screen_img.getpixel((get_dyn_pos_right(1642) + 33*i, get_dyn_y(980)))
                        if px == tuple(self.calibrated_ammo_colour):
                            self.ammo_states[i] = True
                        else:
                            self.ammo_states[i] = False
                    if numberammotoggle:
                        for i in range(6):
                            if self.ammo_states[i]:
                                ammocount = 6 - i
                                self.numberammo_text = f"{ammoprefix}{ammocount}{ammosuffix}"
                                break

                # Health/regen detection
                pixel_colour = self.screen_img.getpixel((get_dyn_x(169), get_dyn_y(977))) #supposed to be #000000
                control_colour = self.screen_img.getpixel((get_dyn_x(176), get_dyn_y(977))) #supposed to be colour of healthbar
                if max(pixel_colour[:3]) <= 3 >= max(self.screen_img.getpixel((get_dyn_x(141), get_dyn_y(955)))[:3]) != control_colour and control_colour[1] >= 55 and not show_UI:
                    # show hud pieces when healthbar is there
                    self.show_health = True
                    self.show_regen = True
                    regen_control_colour = self.screen_img.getpixel((get_dyn_x(141), get_dyn_y(958)))
                    if (regen_control_colour[0] <= maxregencolour[0] and
                        minregencolour[1] <= regen_control_colour[1] <= maxregencolour[1] and
                        regen_control_colour[2] <= maxregencolour[2]):
                        for i in range(200):
                            theta = (2 * math.pi / 200) * -(i+50)
                            x = get_dyn_x(140 + 23 * math.cos(theta))
                            y = get_dyn_y(982 + 23 * math.sin(theta))
                            px = self.screen_img.getpixel((x, y))
                            if (px[0] <= maxregencolour[0] and
                                minregencolour[1] <= px[1] <= maxregencolour[1] and
                                px[2] <= maxregencolour[2]):
                                if regentoggle:
                                    overhealhp = 360-((i)*1.8)
                                    self.regen_extent = int(overhealhp)
                                self.regen_text = f"{regenprefix}{200-i}{regensuffix}"
                                if i >= 198:
                                    self.regen_extent = 0
                                    self.regen_text = f"{regenprefix}0{regensuffix}"
                                break

                    for hp in range(100):
                        px = self.screen_img.getpixel((get_dyn_x(384 - (2*hp)), get_dyn_y(984)))
                        if px == control_colour and px[1] >= 55:
                            self.current_hp = 100-hp
                            break

                    if skulltoggle:
                        self.show_skull_red = (self.current_hp <= lowhealthvar)
                        self.show_skull_green = not self.show_skull_red

                    if numberhealthtoggle:
                        self.health_num_text = f"{healthprefix}{self.current_hp}{healthsuffix}"

                else:
                    # hide hud pieces if healthbar is not there
                    self.show_health = False
                    self.show_regen = False
                    self.health_num_text = ""
                    self.regen_text = f"{regenprefix}0{regensuffix}"
                    self.show_skull_red = False
                    self.show_skull_green = False
                    self.current_hp = 0
                    self.regen_extent = 0

                self.update()
            elif not show_UI:
                # hide hud when game not focused or not running
                self.screen_img = None
                self.ammo_states = [False]*6
                self.numberammo_text = ""
                self.show_overlay = False
                self.show_health = False
                self.show_regen = False
                self.health_num_text = ""
                self.regen_text = f"{regenprefix}0{regensuffix}"
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

        # print(f"{get_dyn_x(140)}x, {get_dyn_y(981)}y")
        
        # overlay image
        if self.show_overlay and overlaytoggle or show_UI and overlaytoggle:
            painter.drawPixmap((self.screen_width - self.overlay_pix.width()) // 2,
                               (self.screen_height - self.overlay_pix.height()) // 2,
                               self.overlay_pix)
        
        #ammo decoration
        if ammodecotoggle and any(self.ammo_states) or show_UI and ammodecotoggle:
            painter.drawPixmap(get_dyn_pos_right(1546), get_dyn_y(919), self.ammo_bg_pix)
        
        # ammo image
        if ammotoggle and any(self.ammo_states) or show_UI and ammotoggle:
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
        if crosshairtoggle and any(self.ammo_states) or show_UI and crosshairtoggle:
            painter.setBrush(QtGui.QColor(crosshaircolour))
            painter.setPen(QtGui.QColor(crosshairoutlinecolour))
            diameter = 4
            painter.drawEllipse(QtCore.QRectF(self.screen_width/2 - diameter/2, self.screen_height/2 - diameter/2, diameter, diameter))
            
        # healthbar polygon
        if healthbartoggle and getattr(self, "current_hp", None) is not None and self.show_health or show_UI and healthbartoggle:
            hp = self.current_hp
            br_x = get_dyn_x(396 - (((396-192)/100)*(100-hp)))
            tr_x = get_dyn_x(380 - (((380-176)/100)*(100-hp)))
            pts = [QtCore.QPointF(get_dyn_x(165),get_dyn_y(973)), QtCore.QPointF(get_dyn_x(181),get_dyn_y(990)), QtCore.QPointF(br_x, get_dyn_y(990)), QtCore.QPointF(tr_x, get_dyn_y(973))]
            poly = QtGui.QPolygonF(pts)
            color = lowhealthcolour if self.current_hp <= lowhealthvar else healthcolour
            painter.setBrush(QtGui.QColor(color))
            painter.setPen(QtCore.Qt.NoPen)
            painter.drawPolygon(poly)
        
        # low health line
        if healthbartoggle and lowhealthvarchanged and show_UI:
            br_x = get_dyn_x(396 - (((396-192)/100)*(100-lowhealthvar)))
            tr_x = get_dyn_x(380 - (((380-176)/100)*(100-lowhealthvar)))
            pen = QtGui.QPen(QtCore.Qt.black, 4)
            painter.setPen(pen)
            painter.drawLine(br_x, get_dyn_y(990), tr_x, get_dyn_y(973))
            pen = QtGui.QPen(QtCore.Qt.red, 2)
            painter.setPen(pen)
            painter.drawLine(br_x, get_dyn_y(990), tr_x, get_dyn_y(973))

        # healthbar decoration
        if healthbardecotoggle and self.healthbar_bg_pix and self.show_health or show_UI and healthbardecotoggle:
            painter.drawPixmap(get_dyn_x(256) - self.healthbar_bg_pix.width()//2, get_dyn_y(982) - self.healthbar_bg_pix.height()//2, self.healthbar_bg_pix)

        # regen meter background + arc + skull
        if regentoggle and self.show_regen or show_UI and regentoggle:
            painter.setBrush(QtGui.QColor(regenbgcolour))
            painter.setPen(QtCore.Qt.NoPen)
            painter.drawEllipse(QtCore.QRectF(get_dyn_x(114), get_dyn_y(954), get_dyn_x(54), get_dyn_y(54)))
            rect = QtCore.QRectF(get_dyn_x(141-27), get_dyn_y(981-27), get_dyn_x(55), get_dyn_y(55))
            start_deg = 90
            span_deg = -self.regen_extent
            start16 = int(start_deg * 16)
            span16 = int(span_deg * 16)
            painter.setBrush(QtGui.QColor(overhealcolour))
            painter.drawPie(rect, start16, span16)
            if self.regen_skull_pix:
                painter.drawPixmap(get_dyn_x(141) - self.regen_skull_pix.width()//2, get_dyn_y(982) - self.regen_skull_pix.height()//2, self.regen_skull_pix)

        # skulls
        if skulltoggle and self.show_health or show_UI and skulltoggle:
            if self.show_skull_green and self.green_skull_pix:
                painter.drawPixmap(get_dyn_x(140) - self.green_skull_pix.width()//2, get_dyn_y(981) - self.green_skull_pix.height()//2, self.green_skull_pix)
            if self.show_skull_red and self.red_skull_pix:
                painter.drawPixmap(get_dyn_x(140) - self.red_skull_pix.width()//2, get_dyn_y(981) - self.red_skull_pix.height()//2, self.red_skull_pix)
        
        # number health
        if numberhealthtoggle and self.health_num_text and self.show_health or show_UI and numberhealthtoggle:
            painter.setPen(QtGui.QColor(numberhealthcolour))
            font_q = QtGui.QFont(font, hpsize)
            painter.setFont(font_q)
            healthrect = make_rect(get_dyn_x(170), get_dyn_y(973), xoffsethealth, yoffsethealth, healthanchor)
            painter.drawText(healthrect, ALIGN_MAP[healthanchor], self.health_num_text)

        # number regen
        if numberregentoggle and self.show_regen or show_UI and numberregentoggle:
            painter.setPen(QtGui.QColor(numberregencolour))
            font_q = QtGui.QFont(font, regensize)
            painter.setFont(font_q)
            regenrect = make_rect(get_dyn_x(100), get_dyn_y(980), xoffsetregen, yoffsetregen, regenanchor)
            painter.drawText(regenrect, ALIGN_MAP[regenanchor], self.regen_text)
            
        # number ammo
        if numberammotoggle and any(self.ammo_states) or show_UI and numberammotoggle:
            painter.setPen(QtGui.QColor(numberammocolour))
            font_q = QtGui.QFont(font, ammosize)
            painter.setFont(font_q)
            ammorect = make_rect(get_dyn_pos_right(1620), get_dyn_y(980), xoffsetammo, yoffsetammo, ammoanchor)
            painter.drawText(ammorect, ALIGN_MAP[ammoanchor], self.numberammo_text)
        painter.end()

def imgui_thread(overlay):
    global lowhealthvar
    global lowhealthcolour
    global healthcolour
    global overhealcolour
    global regenbgcolour
    global numberhealthcolour
    global numberammocolour
    global numberregencolour
    global crosshaircolour
    global crosshairoutlinecolour
    global font
    global ammosize
    global hpsize
    global regensize
    global ammotoggle
    global ammodecotoggle
    global crosshairtoggle
    global healthbartoggle
    global healthbardecotoggle
    global skulltoggle
    global regentoggle
    global overlaytoggle
    global numberhealthtoggle
    global numberammotoggle
    global numberregentoggle
    global healthanchor
    global xoffsethealth
    global yoffsethealth
    global healthoffset
    global ammoanchor
    global xoffsetammo
    global yoffsetammo
    global ammooffset
    global regenanchor
    global xoffsetregen
    global yoffsetregen
    global regenoffset
    #
    global healthprefix
    global healthsuffix
    global ammoprefix
    global ammosuffix
    global regenprefix
    global regensuffix
    global hp_slider
    global regen_slider
    global ammo_slider
    global low_hp_slider
    global lowhealthvarchanged
    global current_font
    
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
        if show_UI:
            # All the healthbar customization options
            imgui.begin("SoT HUD config", flags=imgui.WINDOW_ALWAYS_AUTO_RESIZE |
                                            imgui.WINDOW_NO_SCROLLBAR)
            imgui.begin_tab_bar("MainTabBar")
            if imgui.begin_tab_item("Healthbar")[0]:
                changed, healthbartoggle = imgui.checkbox("Healthbar", healthbartoggle)
                if healthbartoggle:
                    health_rgb = hex_to_rgb_f(healthcolour)
                    changed, health_rgb = imgui.color_edit3("Health colour", *health_rgb)
                    if changed:
                        healthcolour = rgb_f_to_hex(health_rgb)
                    changed, low_hp_slider = imgui.slider_float("Critical health point", low_hp_slider, 0, 100, "%.0f")
                    lowhealthvar = int(low_hp_slider)
                    if imgui.is_item_hovered() or imgui.is_item_active():
                        lowhealthvarchanged = True
                    else:
                        lowhealthvarchanged = False
                    lowhealth_rgb = hex_to_rgb_f(lowhealthcolour)
                    changed, lowhealth_rgb = imgui.color_edit3("Low health colour", *lowhealth_rgb)
                    if changed:
                        lowhealthcolour = rgb_f_to_hex(lowhealth_rgb)
                changed, healthbardecotoggle = imgui.checkbox("Healthbar decorations", healthbardecotoggle)
                changed, numberhealthtoggle = imgui.checkbox("Health number", numberhealthtoggle)
                if numberhealthtoggle:
                    changed, hpsize = imgui.drag_int("Font Size", hpsize, 0.5, 1, 128)
                    changed, healthoffset = imgui.drag_int2("Position", xoffsethealth, yoffsethealth, 1, -screen_width, screen_width)
                    xoffsethealth, yoffsethealth = healthoffset
                    numberhealth_rgb = hex_to_rgb_f(numberhealthcolour)
                    changed, numberhealth_rgb = imgui.color_edit3("", *numberhealth_rgb)
                    if changed:
                        numberhealthcolour = rgb_f_to_hex(numberhealth_rgb)
                    for row_idx, row in enumerate(anchor_grid):
                        for col_idx, anchor in enumerate(row):
                            # Highlight the currently selected anchor
                            if anchor == healthanchor:
                                imgui.push_style_color(imgui.COLOR_BUTTON, 0.3, 0.6, 0.9, 1.0)
                            else:
                                imgui.push_style_color(imgui.COLOR_BUTTON, 0.4, 0.4, 0.4, 1.0)
                            
                            # Draw the button
                            if imgui.button(anchor, width=25, height=25):
                                healthanchor = anchor  # update selected anchor

                            imgui.pop_style_color()
                            if col_idx < len(row) - 1:
                                imgui.same_line()
                    imgui.columns(3, "health_columns", False)  # False disables borders
                    imgui.set_column_width(0, 90)
                    imgui.push_item_width(80)
                    changed, healthprefix = imgui.input_text(" ", healthprefix, 10)
                    imgui.next_column()
                    imgui.set_column_width(1, 30)
                    imgui.text(f"{int(hp_slider)}")
                    imgui.next_column()
                    imgui.set_column_width(2, 136)
                    changed, healthsuffix = imgui.input_text("  ", healthsuffix, 11)
                    imgui.pop_item_width()
                    imgui.next_column()
                    imgui.columns(1)
                changed, hp_slider = imgui.slider_float("Health testing slider", hp_slider, 0, 100, "%.0f")
                imgui.end_tab_item()
                
            if imgui.begin_tab_item("Overheal")[0]:
                changed, regentoggle = imgui.checkbox("Regen meter", regentoggle)
                if regentoggle:
                    overheal_rgb = hex_to_rgb_f(overhealcolour)
                    changed, overheal_rgb = imgui.color_edit3("Overheal colour", *overheal_rgb)
                    if changed:
                        overhealcolour = rgb_f_to_hex(overheal_rgb)
                    regenbg_rgb = hex_to_rgb_f(regenbgcolour)
                    changed, regenbg_rgb = imgui.color_edit3("Background colour", *regenbg_rgb)
                    if changed:
                        regenbgcolour = rgb_f_to_hex(regenbg_rgb)
                changed, skulltoggle = imgui.checkbox("Healthbar skull", skulltoggle)
                changed, numberregentoggle = imgui.checkbox("Overheal number", numberregentoggle)
                if numberregentoggle:
                    changed, regensize = imgui.drag_int("Font Size", regensize, 0.5, 1, 128)
                    changed, regenoffset = imgui.drag_int2("Position", xoffsetregen, yoffsetregen, 1, -screen_width, screen_width)
                    xoffsetregen, yoffsetregen = regenoffset
                    numberregen_rgb = hex_to_rgb_f(numberregencolour)
                    changed, numberregen_rgb = imgui.color_edit3("", *numberregen_rgb)
                    if changed:
                        numberregencolour = rgb_f_to_hex(numberregen_rgb)
                    for row_idx, row in enumerate(anchor_grid):
                        for col_idx, anchor in enumerate(row):
                            # Highlight the currently selected anchor
                            if anchor == regenanchor:
                                imgui.push_style_color(imgui.COLOR_BUTTON, 0.3, 0.6, 0.9, 1.0)
                            else:
                                imgui.push_style_color(imgui.COLOR_BUTTON, 0.4, 0.4, 0.4, 1.0)
                            
                            # Draw the button
                            if imgui.button(anchor, width=25, height=25):
                                regenanchor = anchor  # update selected anchor

                            imgui.pop_style_color()
                            if col_idx < len(row) - 1:
                                imgui.same_line()
                changed, regen_slider = imgui.slider_float("Regen testing slider", regen_slider, 0, 200, "%.0f")
                imgui.end_tab_item()
            if imgui.begin_tab_item("Ammo")[0]:
                changed, ammotoggle = imgui.checkbox("Ammo", ammotoggle)
                changed, ammodecotoggle = imgui.checkbox("Ammo decorations", ammodecotoggle)
                changed, numberammotoggle = imgui.checkbox("Ammo number", numberammotoggle)
                if numberammotoggle:
                    changed, ammosize = imgui.drag_int("Font Size", ammosize, 0.5, 1, 128)
                    changed, ammooffset = imgui.drag_int2("Position", xoffsetammo, yoffsetammo, 1, -screen_width, screen_width)
                    xoffsetammo, yoffsetammo = ammooffset
                    numberammo_rgb = hex_to_rgb_f(numberammocolour)
                    changed, numberammo_rgb = imgui.color_edit3("", *numberammo_rgb)
                    if changed:
                        numberammocolour = rgb_f_to_hex(numberammo_rgb)
                    for row_idx, row in enumerate(anchor_grid):
                        for col_idx, anchor in enumerate(row):
                            # Highlight the currently selected anchor
                            if anchor == ammoanchor:
                                imgui.push_style_color(imgui.COLOR_BUTTON, 0.3, 0.6, 0.9, 1.0)
                            else:
                                imgui.push_style_color(imgui.COLOR_BUTTON, 0.4, 0.4, 0.4, 1.0)
                            
                            # Draw the button
                            if imgui.button(anchor, width=25, height=25):
                                ammoanchor = anchor  # update selected anchor

                            imgui.pop_style_color()
                            if col_idx < len(row) - 1:
                                imgui.same_line()
                changed, ammo_slider = imgui.slider_int("Ammo testing slider", ammo_slider, 0, 6, "%.0f")
                imgui.end_tab_item()
            if imgui.begin_tab_item("Misc")[0]:
                changed, crosshairtoggle = imgui.checkbox("Crosshair", crosshairtoggle)
                if crosshairtoggle:
                    crosshair_rgb = hex_to_rgb_f(crosshaircolour)
                    changed, crosshair_rgb = imgui.color_edit3("Crosshair colour", *crosshair_rgb)
                    if changed:
                        crosshaircolour = rgb_f_to_hex(crosshair_rgb)
                    crosshairoutline_rgb = hex_to_rgb_f(crosshairoutlinecolour)
                    changed, crosshairoutline_rgb = imgui.color_edit3("Crosshair outline colour", *crosshairoutline_rgb)
                    if changed:
                        crosshairoutlinecolour = rgb_f_to_hex(crosshairoutline_rgb)
                changed, overlaytoggle = imgui.checkbox("General overlay", overlaytoggle)
                clicked, current_font = imgui.combo(
                    "Font", current_font, fonts, 30)
                font = fonts[current_font]
                imgui.end_tab_item()
            imgui.end_tab_bar()
            overlay.current_hp = hp_slider
            if hp_slider <= lowhealthvar:
                overlay.show_skull_red = True
                overlay.show_skull_green = False
            else:
                overlay.show_skull_red = False
                overlay.show_skull_green = True
            overlay.health_num_text = f"{healthprefix}{int(hp_slider)}{healthsuffix}"
            overlay.regen_extent = regen_slider * 1.8
            overlay.regen_text = f"{regenprefix}{int(regen_slider)}{regensuffix}"
            overlay.ammo_states = [False] * len(overlay.ammo_states)
            for i in range(5, 5 - ammo_slider, -1):
                overlay.ammo_states[i] = True
            overlay.numberammo_text = f"{ammoprefix}{ammo_slider}{ammosuffix}"
            imgui.end()

        # Render
        imgui.render()
        if show_UI:
            set_clickthrough(hwnd, False)
        else:
            set_clickthrough(hwnd, True)
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)
        time.sleep(1/60)  # ~60 FPS

    impl.shutdown()
    glfw.terminate()

def main():
    # create QApplication first
    app = QtWidgets.QApplication(sys.argv)
    
    # query screen after creating app
    screen_geom = app.primaryScreen().geometry()
    screen_width = screen_geom.width()
    screen_height = screen_geom.height()
    
    # load pixmaps after app exists
    green_skull_pix   = load_pixmap_bytes("Health_Bar_Skull_Green.png", (get_dyn_x(53),get_dyn_y(57)))
    red_skull_pix     = load_pixmap_bytes("Health_Bar_Skull_Red.png", (get_dyn_x(53),get_dyn_y(57)))
    ammo_bg_pix       = load_pixmap_bytes("ammogauge-BG-Frame.png", (get_dyn_x(352),get_dyn_y(126)))
    ammo_pix          = load_pixmap_bytes("ammogauge-pistol-ammunition.png", (get_dyn_x(22),get_dyn_y(22)))
    healthbar_bg_pix  = load_pixmap_bytes("Health_Bar_BG_Frame.png", (get_dyn_x(315),get_dyn_y(100)))
    regen_skull_pix   = load_pixmap_bytes("Regen_Meter_Skull.png", (get_dyn_x(60),get_dyn_y(60)))
    overlay_pix       = load_pixmap_bytes("General_Overlay.png", (get_dyn_x(1920),get_dyn_y(1080)))

    pixmaps = (green_skull_pix, red_skull_pix, ammo_bg_pix, ammo_pix, healthbar_bg_pix, regen_skull_pix, overlay_pix)

    # create and show overlay
    overlay = Overlay(screen_width, screen_height, pixmaps)
    overlay.show()

    # apply native click-through after show()
    overlay.set_click_through_native()
    
    # start imgui thread
    threading.Thread(target=imgui_thread, args=(overlay,), daemon=True).start()
    
    # keyboard hotkeys (global)
    keyboard.add_hotkey('delete', lambda: (print("Exiting..."+("      "*20)), QtCore.QCoreApplication.quit()))
    keyboard.add_hotkey('insert', lambda: globals().__setitem__('show_UI', not globals()['show_UI']))
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
