# ui_imgui.py
import os
import zipfile
import subprocess
import glfw
import imgui
from imgui.integrations.glfw import GlfwRenderer
from OpenGL.GL import *
from config import Config, script_dir
from helpers import hex_to_rgb_f, rgb_f_to_hex
from pixel_utils import get_dyn_x, get_dyn_y
import win32gui
import win32con

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

    impl.shutdown()
    glfw.terminate()