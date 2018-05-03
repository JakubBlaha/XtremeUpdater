from time import sleep
from _thread import start_new
import re
import collections

from theme import PRIM
from wrapper import *
import color as col


def center_window(window):
    "Moves given instance of tk.Tk ot tk.Toplevel window to the center of your screen"

    window.update()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window_width = window.winfo_width()
    window_height = window.winfo_height()

    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)

    window.geometry(f'+{x}+{y}')


def _make_list(obj: [int, float]) -> list:
    _type = type(obj)

    if _type == list:
        return obj

    SUPPORTED = (int, str, tuple)

    if _type not in SUPPORTED:
        raise Exception(f"Cannot convert {_type} to tuple object")

    if isinstance(obj, collections.Iterable) and _type != str:
        return list(obj)

    return [obj]


def fade(wg, cnf={}, ms=10, **kwargs):
    start_new(Reminder._fade, (wg, ms, cnf), kwargs)


class Reminder:
    flash_attr = 'fg'

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
            self._fade(wg, 50, {self.flash_attr: PRIM})
            sleep(.2)

            while self._ishovering(wg):
                sleep(.1)
            self._fade(wg, 20, {self.flash_attr: _attr})
            sleep(.5)

    def _ishovering(self, wg):
        root_x, root_y = wg.winfo_rootx(), wg.winfo_rooty()
        wg_x, wg_y = wg.winfo_width(), wg.winfo_height()
        mouse_x, mouse_y = wg.winfo_pointerx(), wg.winfo_pointery()

        x = mouse_x > root_x and mouse_x < root_x + wg_x
        y = mouse_y > root_y and mouse_y < root_y + wg_y

        return x and y

    @staticmethod
    def _fade(wg, ms, cnf={}, **kwargs):
        kwargs = {**cnf, **kwargs}
        new_kwargs = {}

        for key, value in kwargs.items():
            if not isinstance(value, str):
                continue

            if re.match(r'^#(?:[0-9a-fA-F]{1,2}){3}$', value):
                new_kwargs[key] = value

        kwargs = new_kwargs

        d = {
            attr: [c for c in col.fade(wg[attr], color, ms)]
            for attr, color in kwargs.items()
        }

        for i in range(ms):
            cnf = {attr: d[attr][i] for attr in d.keys()}
            wg.config(**cnf)
            wg.update()
            sleep(.01)


class TextFader:
    to_fade = []

    @staticmethod
    @new_thread
    def fade(wg, text):
        TextFader.to_fade.append([wg, text])

        if len(TextFader.to_fade) - 1:  # If len > 0
            return

        while len(TextFader.to_fade):
            TextFader._fade(TextFader.to_fade[0][0], TextFader.to_fade[0][1])
            del TextFader.to_fade[0]

    @staticmethod
    def _fade(wg, text):
        _orig = wg.cget('fg')

        if wg.cget('text') == '':
            wg.config(fg=wg.cget('bg'))

        else:
            Reminder._fade(wg, 10, fg=wg.cget('bg'))

        wg.config(text=text, fg=wg.cget('bg'))
        
        Reminder._fade(wg, 10, fg=_orig)
