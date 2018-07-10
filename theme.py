# Color palette:
# http://www.color-hex.com/color-palette/46219 (outdated)

BG = "#404d6a"
FG = "#ffffff"
PRIM = "#dbac2a"
SEC = "#232a3a"
DARK = "#10131a"

DISABLED = BG
HOVER = "#131a2a"

from kivy.utils import get_color_from_hex

bg = get_color_from_hex(BG)
fg = get_color_from_hex(FG)
prim = get_color_from_hex(PRIM)
sec = get_color_from_hex(SEC)
dark = get_color_from_hex(DARK)
disabled = get_color_from_hex(DISABLED)
hover = get_color_from_hex(HOVER)

if __name__ == '__main__':
    print(*[item for item in globals().items()], sep='\n')
    input()