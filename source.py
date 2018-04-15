import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
import urllib.request
import os
import sys
import ctypes
from os.path import join
from tkinter import ttk
from time import sleep
from _thread import start_new

from theme import *
from style import *
from cw import center_window
from resources import *
import wgfunc
import customfont


def excepthook(exctype, value, traceback):
    root = tk.Tk()
    root.withdraw()
    tk.messagebox.showerror(
        title="XtremeUpdater | Error",
        message=f"An following unhandled exception has occured!",
        detail=value)


def get_data(url):
    return urllib.request.urlopen(url).read()


def all_children(wid, _class=None):
    _list = wid.winfo_children()

    for item in _list:
        if item.winfo_children():
            _list.extend(item.winfo_children())

    if _class != None:
        for index, wg in enumerate(_list):
            if wg.winfo_class() != _class:
                _list[index] = None

    _list = [i for i in _list if i != None]

    return _list


class DllUpdater:
    domain = "https://github.com/JakubBlaha/XtremeUpdater/blob/master/"
    cache_dir = ".cache"

    def __init__(self):
        self.available_dlls = [
            item for item in get_data(
                os.path.join(self.domain, 'availabledlls.txt') + '?raw=true').decode().split('\n')
        ]

    def __mkdir(self):
        if not os.path.exists(self.cache_dir):
            os.mkdir(self.cache_dir)

    def __download_dll(self, dllname):
        _adress = join(self.domain, 'dll', dllname) + '?raw=true'
        _data = get_data(_adress)
        with open(join(self.cache_dir, dllname), 'wb') as f:
            f.write(_data)

    def __read_dll(self, dllname):
        with open(join(self.cache_dir, dllname), 'rb') as f:
            data = f.read()

        return data

    def __overwrite_dll(self, oldpath, dllname):
        with open(oldpath, 'wb') as f:
            f.write(self.__read_dll(dllname))

    def update_dlls(self, path, dllnames):
        self.__mkdir()
        for dll in dllnames:
            self.__download_dll(dll)
            self.__overwrite_dll(join(path, dll), dll)


class Root(tk.Tk):
    def __init__(self, **kwargs):
        tk.Tk.__init__(self, **kwargs)
        self.attributes("-alpha", 0.0)
        self.iconbitmap(resource_path("img/icon_32.ico"))

        self.top = Window(self)

        self.bind("<Map>", lambda *args: self.top.deiconify())
        self.bind("<Unmap>", lambda *args: self.top.withdraw())
        self.bind("<FocusIn>", lambda *args: self.top.lift())

        self.lift()
        self.top.lift()
        center_window(self.top)
        self.top.attributes("-alpha", 1.0)


class Window(tk.Toplevel):
    def __init__(self, parent=None):
        self.active_tab = "Games"
        self.cont_frm_id = None
        self.last_listbox_item_highlight = -1
        self.listbox_item_height = 20

        def nav_comm(id):
            self.tab_switch(id)

        tk.Toplevel.__init__(self, parent)

        # Window configuration
        self.config(bg=BG, padx=0, pady=0)
        self.title("XtremeUpdater")
        self.transient(parent)
        self.overrideredirect(True)
        self.attributes("-alpha", 0.0)

        # Widget creation
        self.head_frame = tk.Frame(self, width=800, height=32, **frm_cnf)
        self.title_label = tk.Label(
            self.head_frame, text=self.title(), **hlb_cnf)
        self.close_button = tk.Button(
            self.head_frame,
            text="×",
            command=exit,
            **{
                **btn_cnf,
                **btn_head_cnf
            })
        self.minimize_button = tk.Button(
            self.head_frame,
            text="-",
            command=parent.iconify,
            **{
                **btn_cnf,
                **btn_head_cnf
            })
        self.nav_frame = tk.Frame(self, **{**frm_cnf, **nav_frm_cnf})
        self.games_button = tk.Button(
            self.nav_frame,
            text="Games",
            command=lambda: nav_comm("Games"),
            **btn_nav_cnf)
        self.chat_button = tk.Button(
            self.nav_frame,
            text="Chat",
            command=lambda: nav_comm("Chat"),
            **btn_nav_cnf)
        self.system_button = tk.Button(
            self.nav_frame,
            text="System",
            command=lambda: nav_comm("System"),
            **btn_nav_cnf)
        self.cont_canvas = tk.Canvas(self, width=800, height=400, **cnv_cnf)
        self.games_frame = tk.Frame(self, **cont_frm_cnf)
        self.game_path_frame = tk.Frame(self.games_frame, **cont_frm_cnf)
        self.selected_game_label = tk.Label(
            self.game_path_frame, text="Select a game directory", **lb_cnf)
        self.browse_button = tk.Button(
            self.game_path_frame,
            text="\u2026",
            command=self._browse_button_callback,
            **btn_cnf)
        self.dll_frame = tk.Frame(
            self.games_frame, **{
                **cont_frm_cnf,
                **{
                    "padx": 0,
                    "pady": 0,
                    "highlightthickness": 0,
                    "bd": 0
                }
            })
        self.dll_selection_nav_frame = tk.Frame(self.dll_frame, **cont_frm_cnf)
        self.available_updates_label = tk.Label(
            self.dll_selection_nav_frame,
            text="Available dll updates",
            **seclb_cnf)
        self.select_all_button = tk.Button(
            self.dll_selection_nav_frame,
            text="Select all",
            command=self._select_all,
            **btn_cnf)
        self.dll_listbox = tk.Listbox(
            self.dll_frame, width=90, height=13, **listbox_cnf)
        self.listbox_scrollbar = ttk.Scrollbar(
            self.dll_frame, command=self.dll_listbox.yview)
        self.update_button = tk.Button(
            self.games_frame,
            text="Update",
            command=self._update_callback,
            **{
                **btn_cnf,
                **{
                    'font': ('Roboto Bold', 16)
                }
            })
        self.progress_label = tk.Label(
            self.games_frame, text="Follow flashing buttons..")
        self.dll_listbox.config(yscrollcommand=self.listbox_scrollbar.set)
        self.system_frame = tk.Frame(self, **cont_frm_cnf)
        self.spectre_patch_lbframe = tk.LabelFrame(
            self.system_frame,
            text="Spectre and Meltdown patch:",
            **lbfrm_cnf,
            width=300,
            height=120)
        self.spectre_patch_disable = tk.Button(
            self.spectre_patch_lbframe,
            text="Disable",
            command=None,
            **btn_cnf)
        self.spectre_patch_enable = tk.Button(
            self.spectre_patch_lbframe, text="Enable", command=None, **btn_cnf)
        self.spectrewrn_label = tk.Label(
            self.spectre_patch_lbframe,
            text=
            "Disabling spectre patch can exhibit you to attacks from hackers, but it can significantly improve system performance on old CPUs. By right-clicking this label you agree with that we dont have any responsibility on potentional damage caused by attackers!",
            **wrnlb_cnf)

        self.spectre_patch_lbframe.pack_propagate(False)

        # Widget display
        self.head_frame.pack(**head_frm_pck)
        self.title_label.pack(**title_lb_pck)
        self.close_button.pack(**btn_head_pck)
        self.minimize_button.pack(**btn_head_pck)
        self.nav_frame.pack(**nav_frm_pck)
        self.games_button.pack(**btn_nav_pck)
        self.chat_button.pack(**btn_nav_pck)
        self.system_button.pack(**btn_nav_pck)
        self.cont_canvas.pack(**cnv_pck)
        # games frame
        self.game_path_frame.pack(anchor='w', fill='x')
        self.selected_game_label.pack(side='left', fill='x')
        self.browse_button.pack(side='right')
        self.dll_frame.pack(fill='both')
        self.dll_selection_nav_frame.pack(fill='x')
        self.available_updates_label.pack(side='left', anchor='w')
        self.select_all_button.pack(side='right')
        self.dll_listbox.pack(fill='both')
        self.update_button.pack(anchor='e')
        # self.listbox_scrollbar.pack(side='left', fill='y')
        # system frame
        self.spectre_patch_lbframe.pack(anchor="w")
        self.spectrewrn_label.pack()
        self.spectre_patch_disable.pack()
        self.spectre_patch_enable.pack()

        # Bindings
        for btn in all_children(self, 'Button'):
            btn.bind(
                "<Enter>",
                lambda *args, wg=btn: wgfunc.fade(wg, tuple(btn_hover_cnf_cfg.keys()), tuple(btn_hover_cnf_cfg.values()))
            )
            btn.bind(
                "<Leave>",
                lambda *args, wg=btn: wgfunc.fade(wg, tuple(btn_normal_from_hover_cnf_cfg.keys()), tuple(btn_normal_cnf_cfg.values()))
            )

        self.spectrewrn_label.bind(
            "<Button-3>", lambda *args: self.spectrewrn_label.pack_forget())
        # self.dll_frame.bind("<Enter>", lambda *args: self.listbox_scrollbar.pack(side='left', fill='y'))
        self.dll_frame.bind("<Leave>",
                            lambda *args: self.listbox_scrollbar.pack_forget())
        self.dll_listbox.bind("<<ListboxSelect>>",
                              lambda *args: self._update_select_button())
        self.dll_listbox.bind("<Motion>", self._listbox_hover_callback)
        self.dll_listbox.bind("<Leave>", self._listbox_hover_callback)
        self.dll_listbox.bind("<MouseWheel>", self._listbox_hover_callback)

        self.title_label.bind("<Button-1>", self._clickwin)
        self.title_label.bind("<B1-Motion>", self._dragwin)

        # Canvas setup
        self.cont_canvas.create_image(
            -40,
            -40,
            image=get_img("img/acrylic_dark.png"),
            anchor="nw",
            tags="logo")

        self._update_game_path(r"C:/Riot Games/League of Legends/")
        self._disable_unavailable_dlls()
        self._update_select_button()

        reminder.remind(self.browse_button)

    def _get_selection(self):
        selection = [
            self.dll_listbox.get(i) for i in self.dll_listbox.curselection()
        ]
        selection = [
            item for item in selection
            if selection.index(item) not in self.dll_listbox.disabled
        ]

        return selection

    def _update_callback(self):
        dlls = self._get_selection()
        updater.update_dlls(self.path, dlls)
        reminder.remind(self.system_button)

    def _listbox_hover_callback(self, event):
        new_listbox_item_highlight = event.y // self.listbox_item_height + self.dll_listbox.nearest(
            0) + ((-4 if event.delta > 0 else 4) if event.delta != 0 else 0)

        if new_listbox_item_highlight + 1 > self.dll_listbox.size(): return

        if new_listbox_item_highlight != self.last_listbox_item_highlight and self.last_listbox_item_highlight != -1:
            self.dll_listbox.itemconfig(
                self.last_listbox_item_highlight, bg=SEC)

        if new_listbox_item_highlight < 0: return

        if new_listbox_item_highlight not in self.dll_listbox.disabled:
            self.dll_listbox.itemconfig(new_listbox_item_highlight, bg=HOVER)
            self.last_listbox_item_highlight = new_listbox_item_highlight

    def _update_select_button(self):
        """Updates the Select all button automatically based on states of items of dll_listbox"""
        selectable = 0
        for i in range(self.dll_listbox.size()):
            if i not in self.dll_listbox.disabled:
                selectable += 1

        selection = len(self.dll_listbox.curselection())

        if not selectable:
            self.select_all_button.config(text="Select all", state='disabled')
            return

        if selectable <= selection:
            all_selected = True

        else:
            all_selected = False

        if all_selected:
            self.select_all_button.config(
                text="Deselect all",
                command=self._deselect_all,
                state='normal')
        else:
            self.select_all_button.config(
                text="Select all", command=self._select_all, state='normal')

    def _select_all(self):
        """Selects all items in dll_listbox"""
        self.dll_listbox.selection_set(0, 'end')
        self.select_all_button.config(
            text="Deselect all", command=self._deselect_all)

    def _deselect_all(self):
        """Deselects all items in dll_listbox"""
        self.dll_listbox.selection_clear(0, 'end')
        self.select_all_button.config(
            text="Select all", command=self._select_all)

    def _browse_button_callback(self):
        self._update_game_path(self._ask_directory())
        reminder.remind(self.update_button)

    def _ask_directory(self):
        path = tk.filedialog.askdirectory(title="Select game directory")

        return path

    def _update_game_path(self, path):
        """Asks user for a game path and updates everything tied together with it"""
        self.path = path
        ext = ".dll"
        dll_names = [
            name.lower() for name in os.listdir(self.path)
            if os.path.splitext(name)[1] == ext
        ]

        self._update_dll_listbox(dll_names)
        self._disable_unavailable_dlls()
        self._select_all()
        self._update_select_button()

        self.selected_game_label.config(text=os.path.basename(self.path))

    def _update_dll_listbox(self, dll_names):
        """Overwrites dll_listbox items with new ones given in the dll_names parameter"""
        self.dll_listbox.delete(0, 'end')
        self.dll_listbox.disabled = []
        for dll_name in dll_names:
            self.dll_listbox.insert('end', dll_name)

    def _disable_unavailable_dlls(self):
        print(updater.available_dlls)
        for index, dll_name in enumerate(self.dll_listbox.get(0, 'end')):
            if dll_name not in updater.available_dlls:
                self.dll_listbox.itemconfig(
                    index,
                    foreground=DISABLED,
                    background=SEC,
                    selectforeground=DISABLED,
                    selectbackground=SEC)
                self.dll_listbox.disabled.append(index)
            else:
                self.dll_listbox.itemconfig(
                    index,
                    foreground='#dddddd',
                    background=SEC,
                    selectforeground=FG,
                    selectbackground=PRIM)

    def _remove_content_frame(self):
        """Removes active content frame from cont_canvas"""
        self.cont_canvas.delete(self.cont_frm_id)

    def display_cont_frame(self, frame):
        """This function overwrites frame content frame currently disaplayed on the canvas, 
        frame attribute represents a tk.Frame instance which will be displayed on the canvas"""
        self._remove_content_frame()
        self.cont_frm_id = self.cont_canvas.create_window(
            (10, 10),
            window=frame,
            anchor="nw",
            width=self.cont_canvas.winfo_width() - 20,
            height=self.cont_canvas.winfo_height() - 20)

    def logo_animation(self):
        """Animates background image on the canvas"""
        for i in range(50):
            self.cont_canvas.move("logo", -1, -1)
            self.cont_canvas.update()
            sleep(i / 1000)

    def tab_switch(self, id):
        """Displays a frame of given id on cont_canvas"""
        id_frm = {"System": self.system_frame, "Games": self.games_frame}

        try:
            self.display_cont_frame(id_frm[id])

        except KeyError:
            self._remove_content_frame()

        # Navigation bar configuration
        for btn in self.nav_frame.pack_slaves():
            if btn["text"] == id:
                btn.unbind("<Leave>")
                btn.unbind("<Enter>")
                wgfunc.fade(btn, tuple(btn_active_cnf_cfg.keys()),
                            tuple(btn_active_cnf_cfg.values()))

            elif btn["text"] == self.active_tab:
                btn.bind(
                "<Enter>",
                lambda *args, btn=btn: wgfunc.fade(btn, tuple(btn_hover_cnf_cfg.keys()), tuple(btn_hover_cnf_cfg.values()))
                )
                btn.bind(
                "<Leave>",
                lambda *args, btn=btn: wgfunc.fade(btn, tuple(btn_normal_cnf_cfg.keys()), tuple(btn_normal_cnf_cfg.values()))
                )
                wgfunc.fade(btn, tuple(btn_normal_cnf_cfg.keys()),
                            tuple(btn_normal_cnf_cfg.values()))

        self.active_tab = id

        if self.active_tab == 'System' and reminder._current == self.system_button:

            def _():
                reminder.stop()
                sleep(1)
                wgfunc.fade(self.system_button, 'bg', PRIM)

            start_new(_, ())

    def _clickwin(self, event):
        """Prepares variables for _dragwin function"""
        self.offsetx = self.winfo_pointerx() - self.winfo_x()
        self.offsety = self.winfo_pointery() - self.winfo_y()

    def _dragwin(self, event):
        """Updates window position"""
        x = self.winfo_pointerx() - self.offsetx
        y = self.winfo_pointery() - self.offsety
        self.geometry('+%d+%d' % (x, y))


# sys.excepthook = excepthook

customfont.loadfont(resource_path("fnt/Roboto-Regular.ttf"))
customfont.loadfont(resource_path("fnt/Roboto-Light.ttf"))
customfont.loadfont(resource_path("fnt/Roboto-Bold.ttf"))
customfont.loadfont(resource_path("fnt/Roboto-Medium.ttf"))
customfont.loadfont(resource_path("fnt/Roboto-Thin.ttf"))

updater = DllUpdater()
reminder = wgfunc.Reminder()

root = Root()
start_new(root.top.logo_animation, ())
start_new(root.top.tab_switch, (root.top.active_tab, ))

root.mainloop()