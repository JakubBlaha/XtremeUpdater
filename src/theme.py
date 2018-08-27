from yaml import safe_load
from kivy.utils import get_color_from_hex

class Theme:
    DEFAULT_VALUES = {
        'prim': "#dbac2a",
        'sec': "#232a3a",
        'bg': "#131a2a",
        'fg': "#ffffff",
        'dark': "#10131a"
    }

    def __init__(self, values: dict):
        for key, value in {**self.DEFAULT_VALUES, **values}.items():
            setattr(self, key, get_color_from_hex(value))
            setattr(self, key.upper(), value)


try:
    with open('.config/Config.yaml') as f:
        conf = safe_load(f)
except FileNotFoundError:
    NAME = 'default'
else:
    NAME = conf.get('theme', 'default')

with open('theme.yaml') as f:
    themes = safe_load(f)

VALUES = themes.get(NAME, None)
if VALUES == None:
    VALUES = {}

theme = Theme(VALUES)
