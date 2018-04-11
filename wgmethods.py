import color as col
from time import sleep
from _thread import start_new

def cfg_wg(wg, cnf):
    wg.config(**cnf)

def fade(wg, attrs, colors, steps=10):
    def __fade(wg, attrs, colors, __steps):
        if type(attrs) != tuple and type(attrs) != list:
            attrs = (attrs,)
        if type(colors) != tuple and type(colors) != list:
            colors = (colors,)

        d = {}
        for attr, color in zip(attrs, colors):
            d[attr] = [c for c in col.fade(wg[attr], color, __steps)]

        for i in range(__steps):
            cnf = {}
            for attr in list(d.keys()):
                cnf[attr] = d[attr][i]
            wg.config(**cnf)
            wg.update()
            sleep(0.01)
    start_new(__fade, (wg, attrs, colors, steps))

def fade_listbox_item(listbox, index, attrs, colors, steps=10):
    def __fade(listbox, index, attrs, colors, __steps):
        if type(attrs) != tuple and type(attrs) != list:
            attrs = (attrs,)
        if type(colors) != tuple and type(colors) != list:
            colors = (colors,)

        d = {}
        for attr, color in zip(attrs, colors):
            d[attr] = [c for c in col.fade(listbox.itemcget(index, attr), color, __steps)]

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
