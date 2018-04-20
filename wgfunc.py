import color as col
from time import sleep
from _thread import start_new
from theme import PRIM


def _tuple(obj):
    if type(obj) == tuple:
        return obj

    elif type(obj) == list:
        return tuple(obj)

    else:
        return (obj, )


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
        attrs = _tuple(attrs)
        colors = _tuple(colors)

        d = {
            attr: [c for c in col.fade(wg[attr], color, ms)]
            for attr, color in zip(attrs, colors)
        }

        for i in range(ms):
            cnf = {attr: d[attr][i] for attr in list(d.keys())}
            wg.config(**cnf)
            wg.update()
            sleep(0.01)


class Container:
    def __init__(self):
        self.fading = []

    def add_fading(self, wg):
        self.fading.append(wg)

    def remove_fading(self, wg):
        self.fading.remove(wg)

    def is_fading(self, wg):
        return wg in self.fading

    def next_fading(self):
        return self.fading[0]

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

cont = Container()
