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

# constants for regen meter and ammo calibration
minregencolour          = [0, 88, 0]
maxregencolour          = [76, 239, 186]
minammocolour           = [0, 178, 0]
maxhpcolour             = [173, 255, 207]
calibrated_ammo_colour  = (0, 0, 0)

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
    "center":   QtCore.Qt.AlignCenter,                       
}

def make_rect(x, y, xoffset, yoffset, anchor="center"):
    w = h = 500
    half_w, half_h = w // 2, h // 2

    if anchor == "center":
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

# SoT capture
def capture_client(hwnd):
    left, top, right, bot = win32gui.GetClientRect(hwnd)
    w, h = right - left, bot - top
    if w <= 0 or h <= 0:
        raise RuntimeError("Invalid client area")
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
        self.current_hp = None

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
                px = screen_img.getpixel((1772, 980))
                cond = (screen_img.getpixel((1772, 980)) == screen_img.getpixel((1746, 980)) == screen_img.getpixel((1720, 980)) == screen_img.getpixel((1694, 980)) == screen_img.getpixel((1668, 980))) and (px[1] >= 178)
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
            hwnd = win32gui.FindWindow(None, 'Sea of Thieves')
            foreground = win32gui.GetForegroundWindow()
            if hwnd and hwnd == foreground:
                self.screen_img = capture_client(hwnd)
                self.show_overlay = True

                # Ammo detection
                if ammotoggle or crosshairtoggle or numberammotoggle:
                    for i in range(6):
                        px = self.screen_img.getpixel((1642 + (26*i), 980))
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
                pixel_colour = self.screen_img.getpixel((169, 977))
                control_colour = self.screen_img.getpixel((172, 976))
                bar_colour = self.screen_img.getpixel((172, 976))

                if pixel_colour == self.screen_img.getpixel((141, 954)) == (0,0,0) != bar_colour and bar_colour[1] >= 55:
                    # show hud pieces when healthbar is there
                    self.show_health = True
                    self.show_regen = True
                    regen_control_colour = self.screen_img.getpixel((141, 958))
                    if (regen_control_colour[0] <= maxregencolour[0] and
                        minregencolour[1] <= regen_control_colour[1] <= maxregencolour[1] and
                        regen_control_colour[2] <= maxregencolour[2]):
                        for i in range(200):
                            theta = (2 * math.pi / 200) * -(i+50)
                            x = int(140 + 23 * math.cos(theta))
                            y = int(982 + 23 * math.sin(theta))
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
                        px = self.screen_img.getpixel((385 - (2*hp), 984))
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
                    self.current_hp = None

                self.update()
            else:
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
                self.current_hp = None
                self.update()
        except Exception as e:
            print(f" Error capturing screen: {e} (Game is probably starting right now)"+(" "*20), end="\r", flush=True)

    # this is the shit that actually draws all of the HUD parts
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # overlay image
        if self.show_overlay and self.overlay_pix:
            painter.drawPixmap((self.screen_width - self.overlay_pix.width()) // 2,
                               (self.screen_height - self.overlay_pix.height()) // 2,
                               self.overlay_pix)

        # ammo image
        if ammotoggle and any(self.ammo_states):
            for i in range(6):
                x = 1642 + (26*i)
                y = 980
                if self.ammo_states[i] and self.ammo_pix:
                    painter.drawPixmap(x - self.ammo_pix.width()//2, y - self.ammo_pix.height()//2, self.ammo_pix)

        # crosshair
        if crosshairtoggle and any(self.ammo_states):
            painter.setBrush(QtGui.QColor(crosshaircolour))
            painter.setPen(QtGui.QColor(crosshairoutlinecolour))
            cx = self.screen_width // 2
            cy = self.screen_height // 2
            painter.drawEllipse(QtCore.QRectF(cx - 2.5, cy - 2.5, 5, 5))

        # healthbar polygon
        if healthbartoggle and getattr(self, "current_hp", None) is not None and self.show_health:
            hp = self.current_hp
            br_x = 395 - (((395-193)/100)*(100-hp))
            tr_x = 380 - (((380-176)/100)*(100-hp))
            pts = [QtCore.QPointF(167,974), QtCore.QPointF(182,989), QtCore.QPointF(br_x, 990), QtCore.QPointF(tr_x, 974)]
            poly = QtGui.QPolygonF(pts)
            color = lowhealthcolour if self.current_hp <= lowhealthvar else healthcolour
            painter.setBrush(QtGui.QColor(color))
            painter.setPen(QtCore.Qt.NoPen)
            painter.drawPolygon(poly)

        # healthbar decoration
        if healthbardecotoggle and self.healthbar_bg_pix and self.show_health:
            painter.drawPixmap(256 - self.healthbar_bg_pix.width()//2, 982 - self.healthbar_bg_pix.height()//2, self.healthbar_bg_pix)

        # regen meter background + arc + skull
        if regentoggle and self.show_regen:
            painter.setBrush(QtGui.QColor(regenbgcolour))
            painter.setPen(QtCore.Qt.NoPen)
            painter.drawEllipse(QtCore.QRectF(114, 954, 54, 54))
            if self.regen_extent and self.regen_extent != 0:
                rect = QtCore.QRectF(141-26, 981-26, 52, 52)
                start_deg = 90
                span_deg = -self.regen_extent
                start16 = int(start_deg * 16)
                span16 = int(span_deg * 16)
                painter.setBrush(QtGui.QColor(overhealcolour))
                painter.drawPie(rect, start16, span16)
            if self.regen_skull_pix:
                painter.drawPixmap(141 - self.regen_skull_pix.width()//2, 982 - self.regen_skull_pix.height()//2, self.regen_skull_pix)

        # skulls
        if skulltoggle and self.show_health:
            if self.show_skull_green and self.green_skull_pix:
                painter.drawPixmap(140 - self.green_skull_pix.width()//2, 981 - self.green_skull_pix.height()//2, self.green_skull_pix)
            if self.show_skull_red and self.red_skull_pix:
                painter.drawPixmap(140 - self.red_skull_pix.width()//2, 981 - self.red_skull_pix.height()//2, self.red_skull_pix)

        # number health
        if numberhealthtoggle and self.health_num_text and self.show_health:
            painter.setPen(QtGui.QColor(numberhealthcolour))
            font_q = QtGui.QFont(font, hpsize)
            painter.setFont(font_q)
            healthrect = make_rect(170, 973, xoffsethealth, yoffsethealth, healthanchor)
            painter.drawText(healthrect, ALIGN_MAP[healthanchor], self.health_num_text)

        # number regen
        if numberregentoggle and self.show_regen:
            painter.setPen(QtGui.QColor(numberregencolour))
            font_q = QtGui.QFont(font, regensize)
            painter.setFont(font_q)
            regenrect = make_rect(100, 980, xoffsetregen, yoffsetregen, regenanchor)
            painter.drawText(regenrect, ALIGN_MAP[regenanchor], self.regen_text)
            
        # number ammo
        if numberammotoggle and any(self.ammo_states):
            painter.setPen(QtGui.QColor(numberammocolour))
            font_q = QtGui.QFont(font, ammosize)
            painter.setFont(font_q)
            ammorect = make_rect(1620, 980, xoffsetammo, yoffsetammo, ammoanchor)
            painter.drawText(ammorect, ALIGN_MAP[ammoanchor], self.numberammo_text)

        painter.end()

def main():
    # create QApplication first
    app = QtWidgets.QApplication(sys.argv)

    # query screen after creating app
    screen_geom = app.primaryScreen().geometry()
    screen_width = screen_geom.width()
    screen_height = screen_geom.height()

    # load pixmaps after app exists
    green_skull_pix   = load_pixmap_bytes("Health_Bar_Skull_Green.png", (53,57))
    red_skull_pix     = load_pixmap_bytes("Health_Bar_Skull_Red.png", (53,57))
    ammo_pix          = load_pixmap_bytes("ammogauge-pistol-ammunition.png", (18,17))
    healthbar_bg_pix  = load_pixmap_bytes("Health_Bar_BG_Frame.png", (315,100))
    regen_skull_pix   = load_pixmap_bytes("Regen_Meter_Skull.png", (60,60))
    overlay_pix       = load_pixmap_bytes("General_Overlay.png", None)

    pixmaps = (green_skull_pix, red_skull_pix, ammo_pix, healthbar_bg_pix, regen_skull_pix, overlay_pix)

    # create and show overlay
    overlay = Overlay(screen_width, screen_height, pixmaps)
    overlay.show()

    # apply native click-through after show()
    overlay.set_click_through_native()

    # keyboard hotkeys (global)
    keyboard.add_hotkey('f3', lambda: (print("Exiting..."+("     "*20)), QtCore.QCoreApplication.quit()))
    keyboard.add_hotkey('insert', lambda: webbrowser.open("http://localhost:3000"))

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

