# config.py
import os
import json
import zipfile

# base script dir and config path (adjust if you place modules differently)
script_dir = os.path.dirname(os.path.abspath(__file__))
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
    iteration               = 0

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