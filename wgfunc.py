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


def fade_listbox_item(listbox, index, attrs, colors, steps=10):
    def __fade(listbox, index, attrs, colors, __steps):
        if type(attrs) != tuple and type(attrs) != list:
            attrs = (attrs, )
        if type(colors) != tuple and type(colors) != list:
            colors = (colors, )

        d = {}
        for attr, color in zip(attrs, colors):
            d[attr] = [
                c for c in col.fade(
                    listbox.itemcget(index, attr), color, __steps)
            ]

        cont.add_fading(listbox, index)
        for i in range(__steps):
            cnf = {}
            for attr in list(d.keys()):
                cnf[attr] = d[attr][i]
            listbox.itemconfig(index, **cnf)
            listbox.update()
            sleep(0.01)
        cont.remove_fading(listbox, index)

    start_new(__fade, (listbox, index, attrs, colors, steps))


class Reminder:
    flash_attr = 'bg'

    def __init__(self):
        self._current = None

    def remind(self, wg):
        self._current = wg
        start_new(self._remind, (wg, self._current))

    def stop(self):
        self._current = None

    def _remind(self, wg, _foo):
        _attr = wg.cget(self.flash_attr)
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
        self.fading = {}

    def add_fading(self, listbox, index):
        if not listbox in tuple(self.fading.keys()):
            self.fading[listbox] = []
        self.fading[listbox] = self.fading[listbox].append(index)

    def remove_fading(self, listbox, index):
        self.fading[listbox] = self.fading[listbox].remove(index)


cont = Container()
