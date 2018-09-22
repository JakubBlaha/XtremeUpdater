from yaml import safe_load, dump
from kivy.utils import get_color_from_hex
import os


class Theme:
    CONFIG_PATH = '.config/Config.yaml'
    THEME_PATH = 'theme/'
    DEFAULT_VALUES = {
        'prim': "#dbac2a",
        'sec': "#232a3a",
        'bg': "#131a2a",
        'fg': "#ffffff",
        'dark': "#10131a"
    }
    name = 'default'

    def __init__(self, values: dict = {}, name: str = ''):
        if not name:
            with open(self.CONFIG_PATH) as f:
                try:
                    name = safe_load(f)['theme']
                except (FileNotFoundError, KeyError):
                    name = 'default'

        values = values if values else self.get_values(name)

        self.name = name
        for key, value in {**self.DEFAULT_VALUES, **values}.items():
            setattr(self, key, get_color_from_hex(value))
            setattr(self, key.upper(), value)

    @classmethod
    def get_values(cls, theme_name):
        theme_name = theme_name.replace('.yaml', '')
        try:
            with open(cls.THEME_PATH + theme_name + '.yaml') as f:
                return {
                    **cls.DEFAULT_VALUES,
                    **safe_load(f).get(theme_name, {})
                }
        except FileNotFoundError:
            return cls.DEFAULT_VALUES

    @classmethod
    def set_theme(cls, theme_name):
        with open(cls.CONFIG_PATH) as f:
            data = safe_load(f)

        if data.get('theme', '') == theme_name:
            return

        data['theme'] = str(theme_name)

        with open(cls.CONFIG_PATH, 'w') as f:
            dump(data, f)

    @staticmethod
    def decode_theme_name(code: str) -> str:
        return os.path.splitext(code)[0].replace('_', ' ').capitalize()

    @property
    def decoded_name(self) -> str:
        return self.decode_theme_name(self.name)

    @staticmethod
    def encode_theme_name(name: str) -> str:
        return name.replace(' ', '_').lower()

    @property
    def available_themes(self):
        return [
            Theme(name=name)
            for name in os.listdir(self.THEME_PATH)
        ]


theme = Theme()
