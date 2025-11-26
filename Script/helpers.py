# helpers.py
from PyQt5 import QtCore
from pixel_utils import get_dyn_x, get_dyn_y

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

    x = int(x)
    y = int(y)
    xoffset = int(xoffset)
    yoffset = int(yoffset)

    if anchor == "x":
        return QtCore.QRect((x + xoffset) - half_w, (y + yoffset) - half_h, w, h)
    elif anchor == "n":
        return QtCore.QRect((x + xoffset) - half_w, (y + yoffset), w, h)
    elif anchor == "ne":
        return QtCore.QRect((x + xoffset) - w, (y + yoffset), w, h)
    elif anchor == "e":
        return QtCore.QRect((x + xoffset) - w, (y + yoffset) - half_h, w, h)
    elif anchor == "se":
        return QtCore.QRect((x + xoffset) - w, (y + yoffset) - h, w, h)
    elif anchor == "s":
        return QtCore.QRect((x + xoffset) - half_w, (y + yoffset) - h, w, h)
    elif anchor == "sw":
        return QtCore.QRect((x + xoffset), (y + yoffset) - h, w, h)
    elif anchor == "w":
        return QtCore.QRect((x + xoffset), (y + yoffset) - half_h, w, h)
    elif anchor == "nw":
        return QtCore.QRect((x + xoffset), (y + yoffset), w, h)
    else:
        return QtCore.QRect((x + xoffset) - half_w, (y + yoffset) - half_h, w, h)