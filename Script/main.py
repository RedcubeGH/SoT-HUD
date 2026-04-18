# main.py
import sys
import threading
from PyQt5 import QtWidgets
from config import Config, config_path
from pixel_utils import get_sizes
from overlay import Overlay
from ui_imgui import imgui_thread

def main():
    # create QApplication first
    app = QtWidgets.QApplication(sys.argv)
    
    # query screen after creating app
    screen_geom = app.primaryScreen().geometry()
    screen_width = screen_geom.width()
    screen_height = screen_geom.height()
    get_sizes()

    # create and show overlay
    overlay = Overlay(screen_width, screen_height)
    overlay.show()

    # load config
    Config.load_from_file(config_path)
    
    # apply native click-through after show()
    overlay.set_click_through_native()
    
    # start imgui thread
    threading.Thread(target=imgui_thread, args=(overlay,), daemon=True).start()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()