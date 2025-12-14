# overlay.py
import os
import math
from PyQt5 import QtCore, QtGui, QtWidgets
from config import Config, config_path, script_dir
from pixel_utils import get_dyn_x, get_dyn_y, get_dyn_pos_right, get_multiple_pixels, get_sizes
from pixmap_manager import PixmapManager
from watchers import ConfigWatcher
from helpers import make_rect, ALIGN_MAP
import numpy as np
import win32gui
import win32con

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
            hwndqt = int(self.winId())
            exStyle = win32gui.GetWindowLong(hwndqt, win32con.GWL_EXSTYLE)
            exStyle &= ~win32con.WS_EX_APPWINDOW
            exStyle &= ~win32con.WS_EX_TOOLWINDOW
            exStyle |= win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
            win32gui.SetWindowLong(hwndqt, win32con.GWL_EXSTYLE, exStyle)
        except Exception as e:
            print("Failed to set native click-through:", e)

    def update_config(self):
        Config.load_from_file(config_path)
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
        Config.iteration = (Config.iteration + 1) % 10
        if Config.iteration == 0:
            get_sizes()
        # calibration stage
        if Config.calibrated_ammo_colour == (0,0,0):
            self.calibration_label.setText("Pull out a gun with full ammo to calibrate ammo colour")
            self.calibration_label.move((self.screen_width - self.calibration_label.width())//2, self.screen_height - 140)
            self.calibration_label.show()
            QtWidgets.QApplication.processEvents()
            try:
                calibration_coords = [
                    (get_dyn_pos_right(1772), get_dyn_y(980)),
                    (get_dyn_pos_right(1746), get_dyn_y(980)),
                    (get_dyn_pos_right(1720), get_dyn_y(980)),
                    (get_dyn_pos_right(1694), get_dyn_y(980)),
                    (get_dyn_pos_right(1668), get_dyn_y(980))
                ]
                calibration_pixels = get_multiple_pixels(calibration_coords)
                
                if len(calibration_pixels) == 5 and all(px is not None for px in calibration_pixels):
                    px = calibration_pixels[0]
                    cond = (calibration_pixels[0] == calibration_pixels[1]).all() and \
                           (calibration_pixels[1] == calibration_pixels[2]).all() and \
                           (calibration_pixels[2] == calibration_pixels[3]).all() and \
                           (calibration_pixels[3] == calibration_pixels[4]).all() and \
                           (px[1] >= 178)
                    if cond:
                        Config.calibrated_ammo_colour = tuple(int(x) for x in px)
                        self.calibration_label.hide()
                        Config.save_config(False)
            except Exception as e:
                print(f"Couldn't calibrate ammo colour: {e}"+(" "*20), end="\r", flush=True)
            return

        try:
            # only do shit when game running and focused
            foreground = win32gui.GetForegroundWindow()
            if Config.hwnd and Config.hwnd == foreground and not Config.show_UI:
                self.show_overlay = True
                # Batch all pixel coordinates needed
                self.pixel_coords = []
                
                # Ammo pixels
                if Config.ammotoggle or Config.crosshairtoggle or Config.numberammotoggle:
                    ammo_coords = []
                    for i in range(6):
                        x_pos = get_dyn_pos_right(1642) + get_dyn_x(26*i)
                        if self.screen_height == 1440:
                            x_pos = get_dyn_pos_right(1648) + 33*i
                        if self.screen_height == 2160:
                            x_pos = get_dyn_pos_right(1641) + get_dyn_x(26*i)
                        ammo_coords.append((x_pos, get_dyn_y(980)))
                    self.pixel_coords.extend(ammo_coords)
                
                # Health/regen pixels
                health_coords = [
                    (get_dyn_x(169), get_dyn_y(977)),  # pixel_colour
                    (get_dyn_x(176), get_dyn_y(977)),  # control_colour
                    (get_dyn_x(141), get_dyn_y(955)),  # additional check
                    (get_dyn_x(141), get_dyn_y(958))   # regen_control_colour
                ]
                self.pixel_coords.extend(health_coords)
                
                # capture all pixels at once
                self.all_pixels = get_multiple_pixels(self.pixel_coords)
                
                # Process ammo pixels
                if Config.ammotoggle or Config.crosshairtoggle or Config.numberammotoggle and len(self.all_pixels) >= 6:
                    ammo_pixels = self.all_pixels[:6]
                    for i, px in enumerate(ammo_pixels):
                        if px is not None and (px == Config.calibrated_ammo_colour).all():
                            self.ammo_states[i] = True
                        else:
                            self.ammo_states[i] = False
                    
                    if Config.numberammotoggle:
                        for i in range(6):
                            if self.ammo_states[i]:
                                ammocount = 6 - i
                                self.numberammo_text = f"{Config.ammoprefix}{ammocount}{Config.ammosuffix}"
                                break
                
                # Process health pixels
                if len(self.all_pixels) >= 10:               # Make sure we have enough pixels
                    pixel_colour = self.all_pixels[6]        # (169, 977)
                    control_colour = self.all_pixels[7]      # (176, 977)
                    additional_check = self.all_pixels[8]    # (141, 955)
                    regen_control_colour = self.all_pixels[9]# (141, 958)
                    if (pixel_colour[:3].max() <= 18 and 
                        additional_check[:3].max() <= 3 and 
                        not (additional_check[:3] == control_colour[:3]).all() and 
                        control_colour[1] >= 55 and not Config.show_UI):
                        
                        # show hud pieces when healthbar is there
                        self.show_health = True
                        self.show_regen = True
                        
                        if (regen_control_colour[0] <= Config.MAXREGENCOLOUR[0] and
                            Config.MINREGENCOLOUR[1] <= regen_control_colour[1] <= Config.MAXREGENCOLOUR[1] and
                            regen_control_colour[2] <= Config.MAXREGENCOLOUR[2]):
                            
                            # Batch regen circle pixels
                            regen_coords = []
                            for i in range(200):
                                theta = (2 * math.pi / 200) * -(i+50)
                                x = get_dyn_x(140 + 23 * math.cos(theta))
                                y = get_dyn_y(982 + 23 * math.sin(theta))
                                regen_coords.append((x, y))
                            
                            regen_pixels = get_multiple_pixels(regen_coords)
                            
                            for i, px in enumerate(regen_pixels):
                                if px is not None and (px[0] <= Config.MAXREGENCOLOUR[0] and
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

                        # Batch health bar pixels
                        health_coords = []
                        for hp in range(100):
                            health_coords.append((get_dyn_x(384 - (2*hp)), get_dyn_y(984)))
                        
                        health_pixels = get_multiple_pixels(health_coords)
                        
                        for hp, px in enumerate(health_pixels):
                            if px is not None and (px == control_colour).all() and px[1] >= 55:
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
            
        # DEBUGGING
        if Config.debugmenu:
            try:
                painter.setPen(QtGui.QColor("white"))
                font_q = QtGui.QFont(None, 12)
                painter.setFont(font_q)
                debug_text = (
                    f"Window Handle: {Config.hwnd}\n"
                    f"HP: {self.current_hp}\n"
                    f"Ammo States: {self.ammo_states}\n"
                    f"Regen Extent: {self.regen_extent}\n"
                    f"Height: {Config.sot_height}\n"
                    f"Width: {Config.dynright}\n"
                    f"Calibrated Ammo Colour: {Config.calibrated_ammo_colour}\n"
                )
                painter.drawPixmap(400, 5, self.regen_skull_pix)
                painter.drawPixmap(400, 65, self.red_skull_pix)
                painter.drawPixmap(400, 120, self.green_skull_pix)
                painter.drawPixmap(400, 180, self.ammo_pix)
                painter.drawPixmap(400, 240, self.healthbar_bg_pix)
                painter.drawPixmap(400, 300, self.ammo_bg_pix)
                if hasattr(self, 'pixel_coords') and hasattr(self, 'all_pixels'):
                    for i, coord in enumerate(self.pixel_coords):
                        debug_text += f"{coord} : {self.all_pixels[i] if i < len(self.all_pixels) else 'N/A'}\n"

                painter.drawText(2, 50, 1920, 1080,
                    QtCore.Qt.TextWordWrap,
                    debug_text
                )
                
                # Draw red pixels on every pixel coordinate
                for coord in self.pixel_coords:
                    painter.setBrush(QtGui.QColor("red"))
                    painter.setPen(QtCore.Qt.NoPen)
                    painter.drawEllipse(QtCore.QRectF(coord[0] - 2, coord[1] - 2, 4, 4))
                    
                # Draw line from first to last health bar pixel
                if hasattr(self, 'all_pixels') and len(self.all_pixels) >= 10:
                    health_coords = []
                    for hp in range(100):
                        health_coords.append((get_dyn_x(384 - (2*hp)), get_dyn_y(984)))
                    if len(health_coords) >= 2:
                        painter.setPen(QtGui.QPen(QtGui.QColor("red"), 2))
                        painter.drawLine(health_coords[0][0], health_coords[0][1], 
                                    health_coords[-1][0], health_coords[-1][1])
            except Exception:
                pass
        painter.end()