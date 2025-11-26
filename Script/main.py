# main.py
import sys
import threading
import keyboard
from PyQt5 import QtWidgets, QtCore
from config import Config, config_path
from pixel_utils import get_sizes
from overlay import Overlay
from ui_imgui import imgui_thread

def main():
    app = QtWidgets.QApplication(sys.argv)

    # screen geometry
    screen_geom = app.primaryScreen().geometry()
    screen_width = screen_geom.width()
    screen_height = screen_geom.height()

    # initialize sizes and config
    get_sizes()
    Config.load_from_file(config_path)

    # create overlay
    overlay = Overlay(screen_width, screen_height)
    overlay.show()
    overlay.set_click_through_native()

    # start imgui UI in another thread
    threading.Thread(target=imgui_thread, args=(overlay,), daemon=True).start()

    # keyboard hotkeys
    keyboard.add_hotkey('delete', lambda: (print("Exiting..."+("      "*20)), Config.save_config(False), overlay.config_watcher.stop(), QtCore.QCoreApplication.quit()))
    keyboard.add_hotkey('insert', lambda: (setattr(Config, 'show_UI', not Config.show_UI), setattr(overlay, 'regen_extent', 0), setattr(overlay, 'regen_text', f"{Config.regenprefix}0{Config.regensuffix}")))

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()