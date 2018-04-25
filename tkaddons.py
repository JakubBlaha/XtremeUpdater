from time import sleep
from _thread import start_new

from theme import PRIM
import color as col

def center_window(window):
    "Moves given instance of tk.Tk ot tk.Toplevel window to the center of your screen"
    
    window.update()
    screen_width = window.winfo_screenwidth()  # obtaining information
    screen_height = window.winfo_screenheight()
    window_width = window.winfo_width()
    window_height = window.winfo_height()

    x = (screen_width // 2) - (window_width // 2)  # calculating position
    y = (screen_height // 2) - (window_height // 2)

    window.geometry(f'+{x}+{y}')  # setting position; This string formatting works only in python 3.6 and up, you may need to change this line!


def _make_iterable(obj):
    _type = type(obj)
    _iterable = (list, tuple)
    _supported = (int, str)

    if _type in _iterable:
        return obj

    if _type in _supported:
        return (obj,)

    else:
        raise Exception(f"Cannot convert {_type} to tuple object")


def fade(wg, attrs, colors, steps=10):
    start_new(Reminder._fade, (wg, attrs, colors, steps))

class Reminder:
    flash_attr = 'bg'

    def __init__(self):
        self._current = None

    def remind(self, wg):
        if wg != self._current:
            self._current = wg
            start_new(self._remind, (wg, self._current))

    def stop(self):
        self._current = None

    def _remind(self, wg, _foo):
        _attr = wg.cget(self.flash_attr)
        sleep(2)
        while self._current == _foo:
            self._fade(wg, self.flash_attr, PRIM, 50)
            sleep(.2)
            self._fade(wg, self.flash_attr, _attr, 10)
            sleep(.5)

    @staticmethod
    def _fade(wg, attrs, colors, ms):
        attrs = _make_iterable(attrs)
        colors = _make_iterable(colors)

        d = {
            attr: [c for c in col.fade(wg[attr], color, ms)]
            for attr, color in zip(attrs, colors)
        }

        for i in range(ms):
            cnf = {attr: d[attr][i] for attr in list(d.keys())}
            wg.config(**cnf)
            wg.update()
            sleep(0.01)

class TextFader:
    to_fade = []

    @staticmethod
    def fade(wg, text):
        TextFader.to_fade.append([wg, text])

        if len(TextFader.to_fade)-1:
            return

        while len(TextFader.to_fade):
            TextFader._fade(TextFader.to_fade[0][0], TextFader.to_fade[0][1])
            del TextFader.to_fade[0]

    @staticmethod
    def _fade(wg, text):
        _orig = wg.cget('fg')

        if wg.cget('text') != '':
            Reminder._fade(wg, 'fg', wg.cget('bg'), 10)

        wg.config(text=text, fg=wg.cget('bg'))
        Reminder._fade(wg, 'fg', _orig, 10)
