# pixmap_manager.py
import os
from io import BytesIO
from PIL import Image
from PyQt5 import QtGui

class PixmapManager:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.cache = {}

    def load(self, name, size=None):
        key = (name, size)
        if key in self.cache:
            return self.cache[key]
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