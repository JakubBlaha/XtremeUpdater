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
from github import Github

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


class MyGames:
    CFG_FILENAME = 'games.xucfg'

    @staticmethod
    def add(path):
        MyGames._validate_cfg_file()
        with open(MyGames.CFG_FILENAME, 'a') as f:
            f.writelines(path + '\n')

    @staticmethod
    def getall():
        if not MyGames._check_cfg():
            return []

        with open(MyGames.CFG_FILENAME, 'r') as f:
            return [line.replace('\n', '') for line in f]

    @staticmethod
    def clear():
        try:
            os.remove(MyGames.CFG_FILENAME)
        except OSError:
            pass

    @staticmethod
    def _validate_cfg_file():
        if not MyGames._check_cfg():
            MyGames._create_cfg()

    @staticmethod
    def _check_cfg():
        return os.path.exists(os.path.join(os.getcwd(), MyGames.CFG_FILENAME))

    @staticmethod
    def _create_cfg():
        with open(MyGames.CFG_FILENAME, 'w') as f:
            pass


class DllUpdater:
    DOMAIN = "https://github.com/JakubBlaha/XtremeUpdater/blob/master/"
    CACHE_DIR = ".cache"
    GITHUB_TOKEN = "303ba5620e50df340f827c20d2468af8e2001413"
    GITHUB_REPONAME = "XtremeUpdater"
    GITHBU_DLLDIR = "dll"
    available_dlls = []
    running = False

    @staticmethod
    def load_available_dlls():
        g = Github(DllUpdater.GITHUB_TOKEN)
        for repo in g.search_repositories(DllUpdater.GITHUB_REPONAME):
            for _file in repo.get_contents(DllUpdater.GITHBU_DLLDIR):
                DllUpdater.available_dlls.append(_file.name)

    @staticmethod
    def __mkdir():
        if not os.path.exists(DllUpdater.CACHE_DIR):
            os.mkdir(DllUpdater.CACHE_DIR)

    @staticmethod
    def __download_dll(dllname):
        _adress = join(DllUpdater.DOMAIN, 'dll/', dllname) + '?raw=true'
        _data = get_data(_adress)
        with open(join(DllUpdater.CACHE_DIR, dllname), 'wb') as f:
            f.write(_data)

    @staticmethod
    def __read_dll(dllname):
        with open(join(DllUpdater.CACHE_DIR, dllname), 'rb') as f:
            data = f.read()

        return data

    @staticmethod
    def __overwrite_dll(oldpath, dllname):
        with open(oldpath, 'wb') as f:
            f.write(DllUpdater.__read_dll(dllname))

    @staticmethod
    def update_dlls(path, dllnames):
        dll_num = len(dllnames)

        DllUpdater.__mkdir()
        for index, dll in enumerate(dllnames):
            i = index + 1
            window.info(
                f"Downloading {dll} ({i} of {dll_num}) | Please wait..")
            DllUpdater.__download_dll(dll)
            window.info(
                f"Overwriting {dll} ({i} of {dll_num}) | Please wait..")
            DllUpdater.__overwrite_dll(join(path, dll), dll)


class Root(tk.Tk):
    def __init__(self, **kwargs):
        tk.Tk.__init__(self, **kwargs)
        self.attributes("-alpha", 0.0)
        self.iconbitmap(resource_path("img/icon_32.ico"))

    def bind_mapping(self, toplevel):
        self.bind("<Map>", lambda *args: toplevel.deiconify())
        self.bind("<Unmap>", lambda *args: toplevel.withdraw())
        self.bind("<FocusIn>", lambda *args: toplevel.lift())


class Window(tk.Toplevel):
    def __init__(self, parent):
        self.active_tab = "Games"
        self.cont_frm_id = None
        self.last_listbox_item_highlight = -1
        self.listbox_item_height = 20

        tk.Toplevel.__init__(self, parent)

        # Window configuration
        self.config(bg=BG, padx=0, pady=0)
        self.title("XtremeUpdater")
        self.transient(parent)
        self.overrideredirect(True)

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
            command=lambda: self.tab_switch("Games"),
            **btn_nav_cnf)
        self.saved_button = tk.Button(
            self.nav_frame,
            text="Collection",
            command=lambda: self.tab_switch("Collection"),
            **btn_nav_cnf)
        self.system_button = tk.Button(
            self.nav_frame,
            text="System",
            command=lambda: self.tab_switch("System"),
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
        self.dll_frame = tk.Frame(self.games_frame, **{
            **cont_frm_cnf, "padx": 0,
            "pady": 0,
            "highlightthickness": 0,
            "bd": 0
        })
        self.dll_selection_nav_frame = tk.Frame(self.dll_frame, **cont_frm_cnf)
        self.available_updates_label = tk.Label(
            self.dll_selection_nav_frame,
            text="Available dll updates",
            **seclb_cnf)
        self.select_all_button = tk.Button(
            self.dll_selection_nav_frame,
            text="\ue762",
            command=self._select_all,
            state='disabled',
            **btn_cnf)
        self.dll_listbox = tk.Listbox(
            self.dll_frame, width=90, height=13, **listbox_cnf)
        self.listbox_scrollbar = ttk.Scrollbar(
            self.dll_frame, command=self.dll_listbox.yview)
        self.dll_listbox.config(yscrollcommand=self.listbox_scrollbar.set)
        self.update_frame = tk.Frame(self.dll_frame, **{**frm_cnf, 'padx': 0})
        self.update_button = tk.Button(
            self.update_frame,
            text="Update",
            state='disabled',
            command=lambda: start_new(self._update_callback, ()),
            **{
                **btn_cnf, 'font': ('Roboto Bold', 16)
            })
        self.progress_label = tk.Label(self.update_frame, **seclb_cnf)
        self.saved_frame = tk.Frame(self, **cont_frm_cnf)
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
        self.dummy_dll_list = tk.Label(
            self.dll_frame,
            text="\ue8b7\nPlease select a game directory",
            **biglb_cnf)

        self.spectre_patch_lbframe.pack_propagate(False)

        # Widget display
        self.head_frame.pack(**head_frm_pck)
        self.title_label.pack(**title_lb_pck)
        self.close_button.place(x=790, y=0, anchor='ne')
        self.minimize_button.place(x=766, y=0, anchor='ne')
        self.nav_frame.pack(**nav_frm_pck)
        self.games_button.pack(**btn_nav_pck)
        self.saved_button.pack(**btn_nav_pck)
        self.system_button.pack(**btn_nav_pck)
        self.cont_canvas.pack(**cnv_pck)
        # games frame
        self.game_path_frame.pack(anchor='w', fill='x')
        self.selected_game_label.pack(side='left', fill='x')
        self.browse_button.pack(side='right')
        self.dll_selection_nav_frame.pack(fill='x')
        self.available_updates_label.pack(side='left', anchor='w')
        self.select_all_button.pack(side='right')
        self.dll_frame.pack(fill='both', expand=True)
        self.dummy_dll_list.pack(fill='both', expand=True)
        self.update_frame.pack(side='bottom', fill='x')
        self.progress_label.pack(side='left')
        self.update_button.pack(side='right')
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
        self.dll_listbox.bind("<MouseWheel>", self._listbox_scroll_callback)

        self.title_label.bind("<Button-1>", self._clickwin)
        self.title_label.bind("<B1-Motion>", self._dragwin)
        self.dummy_dll_list.bind('<Button-1>', lambda *args: self._browse_button_callback())

        # Canvas setup
        self.cont_canvas.create_image(
            -40,
            -40,
            image=get_img("img/acrylic_dark.png"),
            anchor="nw",
            tags="logo")

        self.info("Follow the flashing buttons | Browse for a directory first")
        reminder.remind(self.browse_button)

    def info(self, text):
        wgfunc.TextFader.fade(self.progress_label, text)

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
        self.update_button.config(state='disabled')
        self.browse_button.config(state='disabled')
        remider.stop()

        dlls = self._get_selection()
        DllUpdater.update_dlls(self.path, dlls)

        self.update_button.config(state='normal')
        self.browse_button.config(state='normal')

        self.info("Updating dlls done | Now we can speed up your system")
        reminder.remind(self.system_button)

    def _listbox_scroll_callback(self, event):
        _new = self.last_listbox_item_highlight + event.delta // abs(
            event.delta) * -4

        self.dll_listbox.itemconfig(self.last_listbox_item_highlight, bg=SEC)
        self.dll_listbox.itemconfig(_new, bg=HOVER)

        self.last_listbox_item_highlight = _new

    def _listbox_hover_callback(self, event):
        new_listbox_item_highlight = event.y // self.listbox_item_height + self.dll_listbox.nearest(
            0)

        if new_listbox_item_highlight != self.last_listbox_item_highlight and self.last_listbox_item_highlight != -1:
            self.dll_listbox.itemconfig(
                self.last_listbox_item_highlight, bg=SEC)

        if new_listbox_item_highlight < 0 or new_listbox_item_highlight + 1 > self.dll_listbox.size(
        ):
            return

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
            self.select_all_button.config(state='disabled')
            return

        if selectable <= selection:
            all_selected = True

        else:
            all_selected = False

        if all_selected:
            self.select_all_button.config(
                command=self._deselect_all, state='normal')
        else:
            self.select_all_button.config(
                command=self._select_all, state='normal')

    def _select_all(self):
        """Selects all items in dll_listbox"""
        self.dll_listbox.selection_set(0, 'end')
        self.select_all_button.config(command=self._deselect_all)

    def _deselect_all(self):
        """Deselects all items in dll_listbox"""
        self.dll_listbox.selection_clear(0, 'end')
        self.select_all_button.config(command=self._select_all)

    def _browse_button_callback(self):
        self.info("Follow the flashing buttons | Now select a directory")
        reminder.stop()
        _path = self._ask_directory()
        if _path == '':
            reminder.remind(self.browse_button)
            return

        start_new(self._update_game_path, (_path, ))

    def _ask_directory(self):
        return tk.filedialog.askdirectory(title="Select game directory")

    def _update_game_path(self, path):
        """Asks user for a game path and updates everything tied together with it"""
        self.dummy_dll_list.unbind('<Button-1>')

        self.info("Looking for dlls..")

        self.path = path
        ext = ".dll"
        dll_names = [
            name.lower() for name in os.listdir(self.path)
            if os.path.splitext(name)[1] == ext
        ]

        self.info("Syncing with server | Please wait..")
        wgfunc.TextFader.fade(self.dummy_dll_list,
                              "\ue895\nLooking for available dll updates..")


        DllUpdater.load_available_dlls()
        self._update_dll_listbox(dll_names)
        self._disable_unavailable_dlls()
        self._select_all()
        self._update_select_button()

        self.dummy_dll_list.pack_forget()
        self.dll_listbox.pack(fill='both')
        self.select_all_button.config(state='normal')
        self.selected_game_label.config(text=os.path.basename(self.path))
        self.update_button.config(state='normal')
        self.info(
            "Follow the flashing buttons | Now let's make your game run faster"
        )
        reminder.remind(self.update_button)

    def _update_dll_listbox(self, dll_names):
        """Overwrites dll_listbox items with new ones given in the dll_names parameter"""
        self.dll_listbox.delete(0, 'end')
        self.dll_listbox.disabled = []
        for dll_name in dll_names:
            self.dll_listbox.insert('end', dll_name)

    def _disable_unavailable_dlls(self):
        for index, dll_name in enumerate(self.dll_listbox.get(0, 'end')):
            if dll_name not in DllUpdater.available_dlls:
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
        id_frm = {
            'System': self.system_frame,
            'Games': self.games_frame,
            'Collection': self.saved_frame
        }

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


if __name__ == '__main__':
    customfont.loadfont(resource_path("fnt/Roboto-Regular.ttf"))
    customfont.loadfont(resource_path("fnt/Roboto-Light.ttf"))
    customfont.loadfont(resource_path("fnt/Roboto-Bold.ttf"))
    customfont.loadfont(resource_path("fnt/Roboto-Medium.ttf"))
    customfont.loadfont(resource_path("fnt/Roboto-Thin.ttf"))

    reminder = wgfunc.Reminder()

    root = Root()
    window = Window(root)
    window.lift()
    center_window(window)
    root.bind_mapping(window)

    start_new(window.logo_animation, ())
    start_new(window.tab_switch, (window.active_tab, ))

    root.mainloop()