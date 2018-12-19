from yaml import safe_load, dump
from kivy.utils import get_color_from_hex
import os

THEME_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'theme/')
DEFAULT_VALUES = {
    'prim': "#dbac2a",
    'sec': "#232a3a",
    'bg': "#131a2a",
    'fg': "#ffffff",
    'dark': "#10131a"
}


class Theme:
    name = 'default'

    def __init__(self, values: dict = {}, name: str = ''):
        self.name = name.replace('.yaml', '')
        values = values if values else self.get_values(self.name)

        for key, value in {**DEFAULT_VALUES, **values}.items():
            setattr(self, key, get_color_from_hex(value))
            setattr(self, key.upper(), value)

    def get_values(self, theme_name=None):
        if not theme_name:
            theme_name = self.name

        theme_name = theme_name.replace('.yaml', '')
        try:
            with open(THEME_PATH + theme_name + '.yaml') as f:
                return {**DEFAULT_VALUES, **safe_load(f).get(theme_name, {})}
        except FileNotFoundError:
            return DEFAULT_VALUES

    def get_values_kivy_color(self, theme_name=None):
        return {
            key: get_color_from_hex(value)
            for key, value in self.get_values(theme_name).items()
        }

    @staticmethod
    def decode_theme_name(code: str) -> str:
        return os.path.splitext(code)[0].replace('_', ' ').replace(
            '.yaml', '').capitalize()

    @property
    def decoded_name(self) -> str:
        return self.decode_theme_name(self.name)

    @staticmethod
    def encode_theme_name(name: str) -> str:
        return name.replace(' ', '_').lower()

    @property
    def available_themes(self):
        return [Theme(name=name) for name in os.listdir(THEME_PATH)]

    @property
    def ordered_available_themes(self):
        l = self.available_themes

        if self.name not in [t.name for t in l]:
            return l

        while l[0].name != self.name:
            l.append(l.pop(0))

        return l
