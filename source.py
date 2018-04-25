import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
import urllib.request
import os
import sys
import ctypes
import yaml
import subprocess
from os.path import join
from tkinter import ttk
from time import sleep
from _thread import start_new
from bs4 import BeautifulSoup
from shutil import copy

from theme import *
from style import *
from resources import *
import tkaddons
import customfont


def run_as_admin(path):
    subprocess.call([
        'powershell',
        f'Start-Process "{path}" -ArgumentList @("Arg1", "Arg2") -Verb RunAs'
    ])


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


class Tweaks:
    def info(fn):
        def wrapper(*args, **kwargs):
            window.info("Running commands | Please wait..")
            fn(*args, **kwargs)
            window.info("Completed | Ready")
        
        return wrapper

    def new_thread(fn):
        def wrapper(*args, **kwargs):
            start_new(fn, args, kwargs)

        return wrapper

    @staticmethod
    @new_thread
    @info
    def spectre_patch_disable():
        run_as_admin('res/spectrepatchdisable.bat')

    @staticmethod
    @new_thread
    @info
    def spectre_patch_enable():
        run_as_admin('res/spectrepatchenable.bat')


class CommonPaths:
    @staticmethod
    def paths():
        # cont = git.file_content('common_paths.json')
        with open('CommonPaths.yaml') as f:
            cont = f.read()

        datastore = yaml.safe_load(cont)

        return [
            os.path.join(os.path.abspath(os.sep), path)
            for path in datastore['paths']
        ]

    @staticmethod
    def names():
        # cont = git.file_content('common_paths.json')
        with open('CommonPaths.yaml') as f:
            cont = f.read()

        datastore = yaml.load(cont)

        return datastore['names']

    @staticmethod
    def local_common_names():
        return [
            name
            for path, name in zip(CommonPaths.paths(), CommonPaths.names())
            if os.path.isdir(
                os.path.join(os.path.splitdrive(os.getcwd())[0], path))
        ]

    @staticmethod
    def names_paths():
        return {
            name: path
            for name, path in zip(CommonPaths.names(), CommonPaths.paths())
        }


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
    URL = "https://github.com/JakubBlaha/XtremeUpdater/tree/master/dll/"
    RAW_URL = "https://github.com/JakubBlaha/XtremeUpdater/raw/master/dll/"
    BACKUP_DIR = ".backup/"
    _available_dlls = []

    @staticmethod
    def load_available_dlls():
        try:
            html = get_data(DllUpdater.URL)

        except:
            window.info(
                "Error while syncing with GitHub | Is your connection ok? Please write us a support request"
            )
            tkaddons.TextFader.fade(window.dummy_dll_list,
                                    "\uEA6A\nSync error")

            return False

        else:
            soup = BeautifulSoup(html, 'html.parser')
            for a in soup.find_all('a', {'class': 'js-navigation-open'}):
                if a.parent.parent.get('class')[0] == 'content':
                    DllUpdater._available_dlls.append(a.text)

            return True

    @staticmethod
    def available_dlls():
        if DllUpdater._available_dlls == []:
            DllUpdater.load_available_dlls()

        return DllUpdater._available_dlls

    @staticmethod
    def _mkbackupdir():
        if not os.path.exists(DllUpdater.BACKUP_DIR):
            os.mkdir(DllUpdater.BACKUP_DIR)

    @staticmethod
    def _download_dll(dllname):
        _adress = join(DllUpdater.RAW_URL, dllname)
        _data = get_data(_adress)

        return _data

    @staticmethod
    def _backup_dlls(path):
        _to_backup = [
            item for item in os.listdir(path)
            if item in DllUpdater.available_dlls()
        ]
        for dll in _to_backup:
            dst = os.path.realpath(
                join(DllUpdater.BACKUP_DIR,
                     os.path.splitdrive(path)[1][1:]))

            if not os.path.exists(dst):
                os.makedirs(dst)

            copy(join(path, dll), dst)

    @staticmethod
    def _overwrite_dll(oldpath, dllname):
        with open(oldpath, 'wb') as f:
            f.write(DllUpdater._read_dll(dllname))

    @staticmethod
    def update_dlls(path, dllnames):
        dll_num = len(dllnames)

        DllUpdater._mkbackupdir()

        window.info("Backing up dlls | Please wait..")
        DllUpdater._backup_dlls(path)

        for index, dll in enumerate(dllnames):
            i = index + 1
            window.info(
                f"Downloading {dll} ({i} of {dll_num}) | Please wait..")
            data = DllUpdater._download_dll(dll)
            window.info(
                f"Overwriting {dll} ({i} of {dll_num}) | Please wait..")
            DllUpdater._overwrite_dll(data)


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
    class ZeroLenDllListError(BaseException):
        pass

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

        self.bind("<FocusIn>", lambda *args: self.lift())
        self.bind("<Button-1>", lambda *args: self.lift())
        self.bind("<Button-2>", lambda *args: self.lift())
        self.bind("<Button-3>", lambda *args: self.lift())

        # Widgets
        self.head = tk.Frame(self, width=800, height=32, **frm_cnf)
        self.title = tk.Label(self.head, text=self.title(), **hlb_cnf)
        self.close = tk.Button(
            self.head, text="×", command=exit, **{
                **btn_cnf,
                **btn_head_cnf
            })
        self.minimize = tk.Button(
            self.head,
            text="-",
            command=parent.iconify,
            **{
                **btn_cnf,
                **btn_head_cnf
            })
        self.navigation = tk.Frame(self, **{**frm_cnf, **nav_frm_cnf})
        self.tab0 = tk.Button(
            self.navigation,
            text="Games",
            command=lambda: self.tab_switch("Games"),
            **btn_nav_cnf)
        self.tab1 = tk.Button(
            self.navigation,
            text="Collection",
            command=lambda: self.tab_switch("Collection"),
            **btn_nav_cnf)
        self.tab2 = tk.Button(
            self.navigation,
            text="System",
            command=lambda: self.tab_switch("System"),
            **btn_nav_cnf)
        self.canvas = tk.Canvas(self, width=800, height=400, **cnv_cnf)
        self.games = tk.Frame(self, **cont_frm_cnf)
        self.dirselection = tk.Frame(self.games, **cont_frm_cnf)
        self.gamename = tk.Label(self.dirselection, **{**lb_cnf, 'fg': SEC})
        self.browse = tk.Button(
            self.dirselection,
            text="\u2026",
            command=self._browse_callback,
            **btn_cnf)
        self.dll_frame = tk.Frame(self.games, **{
            **cont_frm_cnf, "padx": 0,
            "pady": 0,
            "highlightthickness": 0,
            "bd": 0
        })
        self.dll_frame_head = tk.Frame(self.dll_frame, **cont_frm_cnf)
        self.available_updates_label = tk.Label(self.dll_frame_head,
                                                **seclb_cnf)
        self.select_all_button = tk.Button(
            self.dll_frame_head,
            text="\ue762",
            command=self._select_all,
            state='disabled',
            **btn_cnf)
        self.dll_listbox = tk.Listbox(
            self.dll_frame, width=90, height=13, **listbox_cnf)
        self.update_frame = tk.Frame(self.dll_frame, **{**frm_cnf, 'padx': 0})
        self.update_button = tk.Button(
            self.update_frame,
            text="Update",
            state='disabled',
            command=lambda: start_new(self._update_callback, ()),
            **{
                **btn_cnf, 'font': ('Roboto Bold', 16)
            })
        self.progress_label = tk.Label(self.canvas, anchor='w', height=2, **seclb_cnf)
        self.collection_frame = tk.Frame(self, **cont_frm_cnf)
        self.collectionlabel0 = tk.Label(
            self.collection_frame, text="Detected games", **seclb_cnf)
        self.commonpaths_listbox = tk.Listbox(
            self.collection_frame,
            width=90,
            height=13,
            **{
                **listbox_cnf, 'selectmode': 'single'
            })
        self.system = tk.Frame(self, **cont_frm_cnf)
        self.spectre_patch_lbframe = tk.LabelFrame(
            self.system,
            text="Spectre and Meltdown patch:",
            **lbfrm_cnf,
            width=300,
            height=120)
        self.spectre_patch_disable = tk.Button(
            self.spectre_patch_lbframe,
            text="Disable",
            command=Tweaks.spectre_patch_disable,
            **btn_cnf)
        self.spectre_patch_enable = tk.Button(
            self.spectre_patch_lbframe,
            text="Enable",
            command=Tweaks.spectre_patch_enable,
            **btn_cnf)
        self.spectrewrn_label = tk.Label(
            self.spectre_patch_lbframe,
            text=
            "Disabling spectre patch can exhibit you to attacks from hackers, but it can significantly improve system performance on old CPUs. By right-clicking this label you agree with that we dont have any responsibility on potentional damage caused by attackers!",
            **wrnlb_cnf)
        self.dummy_dll_list = tk.Label(
            self.dll_frame,
            text="\ue8b7\nPlease select a game directory",
            **biglb_cnf)
        self.favorite = tk.Button(
            self.navigation,
            text="\ue735",
            command=lambda: self.tab_switch("\ue735"),
            **{
                **btn_nav_cnf, 'width': 1,
                'font': ('Segoe MDL2 Assets', 14)
            })
        self.favorite_frame = tk.Frame(self, **cont_frm_cnf)

        self.spectre_patch_lbframe.pack_propagate(False)

        self.head.pack(**head_frm_pck)
        self.title.pack(**title_lb_pck)
        self.close.place(x=790, y=0, anchor='ne')
        self.minimize.place(x=766, y=0, anchor='ne')
        self.navigation.pack(**nav_frm_pck)
        self.tab0.pack(**btn_nav_pck)
        self.tab1.pack(**btn_nav_pck)
        self.tab2.pack(**btn_nav_pck)
        self.favorite.pack(**{**btn_nav_pck, 'side': 'right', 'ipadx': 20})
        self.canvas.pack(**cnv_pck)
        # Games
        self.dirselection.pack(anchor='w', fill='x')
        self.gamename.pack(side='left', fill='x')
        self.browse.pack(side='right')
        self.dll_frame_head.pack(fill='x')
        self.available_updates_label.pack(side='left', anchor='w')
        self.select_all_button.pack(side='right')
        self.dll_frame.pack(fill='both', expand=True)
        self.dummy_dll_list.pack(fill='both', expand=True)
        self.update_frame.pack(side='bottom', fill='x')
        self.update_button.pack(side='right')
        # Collection
        self.collectionlabel0.pack(anchor='w')
        self.commonpaths_listbox.pack(fill='both')
        # System
        self.spectre_patch_lbframe.pack(anchor="w", pady=10, padx=10)
        self.spectrewrn_label.pack()
        self.spectre_patch_disable.pack()
        self.spectre_patch_enable.pack()

        self.canvas.create_window(
            (10, int(self.canvas['height']) - 40),
            window=self.progress_label,
            anchor='nw',
            width=int(self.canvas['width']) - 20)

        for w in all_children(self):
            if type(w) == tk.Frame and all_children(w) == []:
                dummy = tk.Label(
                    w, text="\ue822\nUnder construction..", **biglb_cnf)
                dummy.pack(expand=True, fill='both')

        # Bindings
        for btn in all_children(self, 'Button'):
            btn.bind(
                "<Enter>",
                lambda *args, wg=btn: tkaddons.fade(wg, tuple(btn_hover_cnf_cfg.keys()), tuple(btn_hover_cnf_cfg.values()))
            )
            btn.bind(
                "<Leave>",
                lambda *args, wg=btn: tkaddons.fade(wg, tuple(btn_normal_from_hover_cnf_cfg.keys()), tuple(btn_normal_cnf_cfg.values()))
            )

        self.spectrewrn_label.bind(
            "<Button-3>", lambda *args: self.spectrewrn_label.pack_forget())
        self.dll_listbox.bind("<<ListboxSelect>>",
                              lambda *args: self._update_select_button())
        self.dll_listbox.bind("<Motion>", self._listbox_hover_callback)
        self.dll_listbox.bind("<Leave>", self._listbox_hover_callback)
        self.dll_listbox.bind("<MouseWheel>", self._listbox_scroll_callback)

        self.title.bind("<Button-1>", self._clickwin)
        self.title.bind("<B1-Motion>", self._dragwin)

        self.commonpaths_listbox.bind("<<ListboxSelect>>",
                                      self._common_path_listbox_callback)

        # Canvas setup
        self.canvas.create_image(
            -40,
            -40,
            image=get_img("img/acrylic_dark.png"),
            anchor="nw",
            tags="logo")

        self.load_common_paths()

        self.info("Follow the blinking buttons | Browse for a directory first")
        reminder.remind(self.browse)

    def _common_path_listbox_callback(self, *args):
        self.tab_switch('Games')
        start_new(
            self._update_game_path,
            (CommonPaths.names_paths()[self.commonpaths_listbox.get('active')],
             ))

    def load_common_paths(self):
        for i in CommonPaths.local_common_names():
            self.commonpaths_listbox.insert(0, i)

    def info(self, text):
        start_new(tkaddons.TextFader.fade, (self.progress_label, text))

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
        self.browse.config(state='disabled')
        self.dummy_dll_list.pack(expand=True)
        self.dll_listbox.pack_forget()
        tkaddons.TextFader.fade(self.dummy_dll_list,
                                "\ue896\nUpdating your dlls..")
        reminder.stop()

        dlls = self._get_selection()
        DllUpdater.update_dlls(self.path, dlls)

        self.update_button.config(state='normal')
        self.browse.config(state='normal')

        tkaddons.TextFader.fade(self.dummy_dll_list, "\ue930\nCompleted")
        sleep(2)
        tkaddons.TextFader.fade(self.dummy_dll_list,
                                "\ue8b7\nPlease select a game directory")
        self.info("Updating dlls done | Now we can speed up your system")
        reminder.remind(self.tab2)

    def _listbox_scroll_callback(self, event):
        _new = self.last_listbox_item_highlight + event.delta // abs(
            event.delta) * -4

        s = self.dll_listbox.size()
        if _new <= self.dll_listbox.size(
        ) - 1 and _new > -1 and self.dll_listbox.nearest(
                0) != 0 and self.dll_listbox.nearest(s) != s - 10:
            self.dll_listbox.itemconfig(
                self.last_listbox_item_highlight, bg=SEC)
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
        self.commonpaths_listbox.unbind(
            "<<ListboxSelect>>"
        )  # -------------------------------------------------------------| - hotfix (probably tkinter library issue)
        self.dll_listbox.selection_set(  #                                  |
            0, 'end')  #                                                  |
        self.commonpaths_listbox.bind(  #                                   |
            "<<ListboxSelect>>", self._common_path_listbox_callback)  # - |
        self.select_all_button.config(command=self._deselect_all)

    def _deselect_all(self):
        """Deselects all items in dll_listbox"""
        self.dll_listbox.selection_clear(0, 'end')
        self.select_all_button.config(command=self._select_all)

    def _browse_callback(self):
        self.info("Follow the blinking buttons | Now select a directory")
        reminder.stop()
        _path = self._ask_directory()
        if _path == '':
            reminder.remind(self.browse)
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

        if self.dll_listbox in self.dll_frame.pack_slaves():
            self.dummy_dll_list.config(text='')

        self.dll_listbox.pack_forget()
        self.dummy_dll_list.pack(fill='both', expand=True)
        self.info("Syncing with server | Please wait..")
        tkaddons.TextFader.fade(self.dummy_dll_list,
                                "\ue895\nLooking for available dll updates..")

        try:
            self._update_dll_listbox(dll_names)

        except self.ZeroLenDllListError:
            return

        self._disable_unavailable_dlls()
        self._select_all()
        self._update_select_button()

        self.dummy_dll_list.pack_forget()
        self.dll_listbox.config(
            bg=cont_frm_cnf['bg'], highlightbackground=cont_frm_cnf['bg'])
        self.dll_listbox.pack(fill='both')
        tkaddons.fade(self.dll_listbox, ('bg', 'highlightbackground'),
                      (listbox_cnf['bg'], listbox_cnf['highlightbackground']))

        self.select_all_button.config(state='normal')
        tkaddons.TextFader.fade(self.gamename, self.path)
        tkaddons.TextFader.fade(self.available_updates_label,
                                "Available dll updates")
        self.update_button.config(state='normal')
        self.info(
            "Follow the blinking buttons | Now let's make your game run faster"
        )
        reminder.remind(self.update_button)

    def _update_dll_listbox(self, dll_names):
        """Overwrites dll_listbox items with new ones given in the dll_names parameter"""
        if len(dll_names) == 0:
            self.dll_listbox.pack_forget()
            self.dummy_dll_list.config(text='')
            self.dummy_dll_list.pack(fill='both', expand=True)
            tkaddons.TextFader.fade(self.dummy_dll_list,
                                    "\ue783\nNo dlls found in this directory")

            self.info(
                "We have not found any dlls in this directory | Please select another one"
            )

            raise self.ZeroLenDllListError

        self.dll_listbox.delete(0, 'end')
        self.dll_listbox.disabled = []
        for dll_name in dll_names:
            self.dll_listbox.insert('end', dll_name)

    def _disable_unavailable_dlls(self):
        for index, dll_name in enumerate(self.dll_listbox.get(0, 'end')):
            if dll_name not in DllUpdater.available_dlls():
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
        """Removes active content frame from canvas"""
        self.canvas.delete(self.cont_frm_id)

    def display_cont_frame(self, frame):
        """This function overwrites frame content frame currently disaplayed on the canvas, 
        frame attribute represents a tk.Frame instance which will be displayed on the canvas"""
        self._remove_content_frame()
        self.cont_frm_id = self.canvas.create_window(
            (10, 10),
            window=frame,
            anchor="nw",
            width=self.canvas.winfo_width() - 20,
            height=self.canvas.winfo_height() - 51)

    def logo_animation(self):
        """Animates background image on the canvas"""
        for i in range(50):
            self.canvas.move("logo", -1, -1)
            self.canvas.update()
            sleep(i / 1000)

    def tab_switch(self, id):
        """Displays a frame of given id on canvas"""
        id_frm = {
            'System': self.system,
            'Games': self.games,
            'Collection': self.collection_frame,
            '\ue735': self.favorite_frame
        }

        try:
            self.display_cont_frame(id_frm[id])

        except KeyError:
            self._remove_content_frame()

        # Navigation bar configuration
        for btn in self.navigation.pack_slaves():
            if btn["text"] == id:
                btn.unbind("<Leave>")
                btn.unbind("<Enter>")
                tkaddons.fade(btn, tuple(btn_active_cnf_cfg.keys()),
                              tuple(btn_active_cnf_cfg.values()))

            elif btn["text"] == self.active_tab:
                btn.bind(
                "<Enter>",
                lambda *args, btn=btn: tkaddons.fade(btn, tuple(btn_hover_cnf_cfg.keys()), tuple(btn_hover_cnf_cfg.values()))
                )
                btn.bind(
                "<Leave>",
                lambda *args, btn=btn: tkaddons.fade(btn, tuple(btn_normal_cnf_cfg.keys()), tuple(btn_normal_cnf_cfg.values()))
                )
                tkaddons.fade(btn, tuple(btn_normal_cnf_cfg.keys()),
                              tuple(btn_normal_cnf_cfg.values()))

        self.active_tab = id

        if self.active_tab == 'System' and reminder._current == self.tab2:

            def _():
                reminder.stop()
                sleep(1)
                tkaddons.fade(self.tab2, 'bg', PRIM)

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

    reminder = tkaddons.Reminder()

    root = Root()
    window = Window(root)
    window.lift()
    tkaddons.center_window(window)
    root.bind_mapping(window)

    start_new(window.logo_animation, ())
    start_new(window.tab_switch, (window.active_tab, ))

    root.mainloop()
