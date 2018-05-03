# TODO
# Fade title when window losts focus
# Clean up style.py
# Clean up code
# Think of better variable names :)

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
from nop import NOP

from theme import *
from resources import *
from wrapper import *
from style import *
import tkaddons
import customfont
import color


def run_as_admin(path):
    window.info("Elevation necessary | Please confirm UAC dialog..")
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


class SyncError(BaseException):
    pass


class Tweaks:
    def info(fn):
        def wrapper(*args, **kwargs):
            window.info("Running commands | Please wait..")
            fn(*args, **kwargs)
            window.info("Completed | Ready")

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
    _datastore = None

    @staticmethod
    def datastore() -> dict:
        if CommonPaths._datastore != None:
            return CommonPaths._datastore

        gui.info("Syncing with GitHub | Please wait..")

        data = get_data(
            'https://github.com/jakubblaha/xtremeupdater/raw/master/res/CommonPaths.yaml'
        )
        data = data.decode()

        datastore = yaml.safe_load(data)

        CommonPaths._datastore = datastore

        return datastore

    @staticmethod
    def local_common_names() -> list:
        local = []
        datastore = CommonPaths.datastore()
        for game in datastore:
            for path in datastore[game]:
                path = os.path.join(os.path.splitdrive(os.getcwd())[0], path)
                if os.path.isdir(path):
                    local.append(game)

        return local

    @staticmethod
    def get_path(game: str) -> str:
        datastore = CommonPaths.datastore()

        paths = datastore.get(game, [])

        if len(paths) == 0:
            raise Exception(f"No paths found for {game}")

        if len(paths) > 1:
            #TODO
            raise Exception(f"Multiple paths for {game} found: {paths}")

        return paths[0]


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
            raise SyncError

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
    def _backup_dlls(path, dlls):
        _to_backup = [item for item in os.listdir(path) if item in dlls]
        for dll in _to_backup:
            dst = os.path.realpath(
                join(DllUpdater.BACKUP_DIR,
                     os.path.splitdrive(path)[1][1:]))

            if not os.path.exists(dst):
                os.makedirs(dst)

            copy(join(path, dll), dst)

    @staticmethod
    def _overwrite_dll(path, data):
        with open(path, 'wb') as f:
            f.write(data)

    @staticmethod
    def update_dlls(path, dlls):
        dll_num = len(dlls)

        DllUpdater._mkbackupdir()

        gui.info("Backing up dlls | Please wait..")
        DllUpdater._backup_dlls(path, dlls)

        for index, dll in enumerate(dlls):
            i = index + 1
            gui.info(f"Downloading {dll} ({i} of {dll_num}) | Please wait..")
            data = DllUpdater._download_dll(dll)
            gui.info(f"Overwriting {dll} ({i} of {dll_num}) | Please wait..")
            DllUpdater._overwrite_dll(join(path, dll), data)

    @staticmethod
    def restore_dlls(path, dlls):
        gui.info("Restoring | Please wait..")

        dll_num = len(dlls)
        bck_path = os.path.abspath(
            join(DllUpdater.BACKUP_DIR,
                 os.path.splitdrive(path)[1][1:]))

        _restored = 0
        for index, dll in enumerate(dlls):
            i = index + 1

            backed_dll_path = join(bck_path, dll)
            try:
                copy(backed_dll_path, path)
            except:
                pass
            else:
                _restored += 1

        gui.info(f"Restoring done | Restored {_restored} of {dll_num} dlls")

    @staticmethod
    def available_restore(path):
        bck_path = os.path.abspath(join(DllUpdater.BACKUP_DIR, path))

        return os.listdir(bck_path)


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

    class ButtonNav(tk.Button):
        def __init__(self, window_instance, *args, **kwargs):
            if not isinstance(window_instance, Window):
                raise TypeError(
                    "window parameter must be an instance of the Window class")

            command = lambda: window_instance.tab_switch(kwargs.get('text', ''))
            width = 12
            font = ['Roboto', 14, 'bold']

            if len(kwargs.get('text', '')) == 1:
                font.remove('bold')
                width = 1

            kwargs = {
                **btn, 'command': command,
                'font': font,
                'width': width,
                **kwargs
            }

            tk.Button.__init__(self, *args, kwargs)

    class FrameTab(tk.Frame):
        def __init__(self, window_instance, *args, **kwargs):
            if not isinstance(window_instance, Window):
                raise TypeError(
                    "window parameter must be an instance of the Window class")

            kwargs = {**frm_cnf, **kwargs}

            tk.Frame.__init__(self, *args, kwargs)

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
        self.head = tk.Frame(self, frm_cnf, width=800, height=32)
        self.title = tk.Label(self.head, hlb_cnf, text=self.title())
        self.close = tk.Button(
            self.head, text="×", command=parent.destroy, cnf=btn_head)
        self.minimize = tk.Button(
            self.head, text="-", command=parent.iconify, cnf=btn_head)
        self.navigation = tk.Frame(self, frm_cnf)
        self.tab0 = self.ButtonNav(self, self.navigation, text='Games')
        self.tab1 = self.ButtonNav(self, self.navigation, text='Collection')
        self.tab2 = self.ButtonNav(self, self.navigation, text='System')

        self.canvas = tk.Canvas(self, cnv_cnf, width=800, height=400)
        self.games = tk.Frame(self, **frm_cnf)
        self.dirselection = tk.Frame(self.games, **frm_cnf)
        self.gamename = tk.Label(self.dirselection, **{**lb_cnf, 'fg': SEC})
        global btn
        self.browse = tk.Button(
            self.dirselection,
            text="\uE8B7",
            command=self._browse_callback,
            height=2,
            **btn)
        self.dll_frame = tk.Frame(self.games, **{
            **frm_cnf, "padx": 0,
            "pady": 0,
            "highlightthickness": 0,
            "bd": 0
        })
        self.dll_frame_head = tk.Frame(self.dll_frame, **frm_cnf)
        self.available_updates_label = tk.Label(self.dll_frame_head,
                                                **seclb_cnf)
        self.select_all_button = tk.Button(
            self.dll_frame_head,
            text="\ue762",
            command=self._selectall_callback,
            state='disabled',
            **btn)
        self.dll_listbox = tk.Listbox(
            self.dll_frame, width=90, height=13, **listbox_cnf)
        self.update_frame = tk.Frame(self.dll_frame, **{**frm_cnf, 'padx': 0})
        self.update_button = tk.Button(
            self.update_frame,
            text="Update",
            state='disabled',
            command=self._update_callback,
            anchor='s',
            **{
                **btn, 'font': ('Roboto Bold', 16)
            })
        self.restore_button = tk.Button(
            self.update_frame,
            text="Restore",
            state='disabled',
            command=self._restore_callback,
            anchor='s',
            **{
                **secbtn, 'font': ('Roboto Bold', 11)
            })
        self.progress_label = tk.Label(
            self.canvas, anchor='w', height=2, **seclb_cnf)
        self.collection_frame = tk.Frame(self, **frm_cnf)
        self.collectionlabel0 = tk.Label(
            self.collection_frame, text="Detected games", **seclb_cnf)
        self.commonpaths_listbox = tk.Listbox(
            self.collection_frame,
            width=90,
            height=13,
            **{
                **listbox_cnf, 'selectmode': 'single',
                'bg': DARK
            })
        self.system = tk.Frame(self, **frm_cnf)
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
            **btn)
        self.spectre_patch_enable = tk.Button(
            self.spectre_patch_lbframe,
            text="Enable",
            command=Tweaks.spectre_patch_enable,
            **btn)
        self.spectrewrn_label = tk.Label(
            self.spectre_patch_lbframe,
            text=
            "Disabling spectre patch can exhibit you to attacks from hackers, but it can significantly improve system performance on old CPUs. By right-clicking this label you agree with that we dont have any responsibility on potentional damage caused by attackers!",
            **wrnlb_cnf)
        self.dummy_dll_list = tk.Label(
            self.dll_frame,
            text="\ue8b7\nPlease select a game directory",
            **biglb_cnf)
        self.favorite = self.ButtonNav(self, self.navigation, text="\ue734")
        self.favorite_frame = tk.Frame(self, **frm_cnf)
        self.settings = self.ButtonNav(self, self.navigation, text="\ue115")
        self.settings_frame = tk.Frame(self, **frm_cnf)

        self.spectre_patch_lbframe.pack_propagate(False)

        self.head.pack(**head_frm_pck)
        self.title.pack(**title_lb_pck)
        self.close.place(x=790, y=0, anchor='ne')
        self.minimize.place(x=766, y=0, anchor='ne')
        self.navigation.pack(**nav_frm_pck)
        self.tab0.pack(**btn_nav_pck)
        self.tab1.pack(**btn_nav_pck)
        self.tab2.pack(**btn_nav_pck)
        self.settings.pack(**{**btn_nav_pck, 'side': 'right', 'ipadx': 10})
        self.favorite.pack(**{**btn_nav_pck, 'side': 'right', 'ipadx': 10})
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
        self.restore_button.pack(side='right', fill='y')
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
        for wg in all_children(self, 'Button'):
            wg.bind(
                "<Enter>", lambda *args, wg=wg: tkaddons.fade(wg, btn_hover))
            wg.bind("<Leave>", lambda *args, wg=wg: tkaddons.fade(wg, btn))

        self.spectrewrn_label.bind(
            "<Button-3>", lambda *args: self.spectrewrn_label.pack_forget())
        self.dll_listbox.bind("<<ListboxSelect>>",
                              lambda *args: self._listboxselection_callback())
        self.dll_listbox.bind("<Motion>", self._listbox_hover_callback)
        self.dll_listbox.bind("<Leave>", self._listbox_hover_callback)
        self.dll_listbox.bind("<MouseWheel>", self._listbox_scroll_callback)

        self.title.bind("<Button-1>", self._clickwin)
        self.title.bind("<B1-Motion>", self._dragwin)

        # Canvas setup
        img_path = 'img/acrylic_dot.png'
        img = get_img(img_path, _type='PIL')
        pix = img.load()
        bg_color = pix[0, 0]
        bg_color = color.rgb_to_hex(bg_color)
        self.canvas.config(bg=bg_color)
        tk_img = tkimage(img)
        self.canvas.create_image(
            0, 0, image=tk_img, anchor="center", tags="logo")

        self._load_common_paths()

        self.info("Follow the blinking buttons | Browse for a directory first")
        reminder.remind(self.browse)

    @new_thread
    def _restore_callback(self):
        DllUpdater.restore_dlls(self.path, self._get_dll_selection())

    def _common_path_listbox_callback(self, *args):
        self.tab_switch('Games')

        path = CommonPaths.get_path(self.commonpaths_listbox.get('active'))
        self._update_game_path(path)

    @new_thread
    def _load_common_paths(self):
        self.wait_visibility(self.commonpaths_listbox)

        local_games = CommonPaths.local_common_names()

        tkaddons.fade(self.commonpaths_listbox, bg=listbox_cnf['bg'])
        self.commonpaths_listbox.bind("<<ListboxSelect>>",
                                      self._common_path_listbox_callback)

        if len(local_games) == 0:
            self.info("Syncing done | No games detected")
            return

        for i in local_games:
            self.commonpaths_listbox.insert(0, i)

        self.info("Syncing done | Select your game")

    def info(self, text):
        tkaddons.TextFader.fade(self.progress_label, text)

    def _get_dll_selection(self):
        selection = [
            self.dll_listbox.get(i) for i in self.dll_listbox.curselection()
        ]
        selection = [
            item for item in selection
            if selection.index(item) not in self.dll_listbox.disabled
        ]

        return selection

    @new_thread
    def _reset_tab0(self):
        sleep(2)
        tkaddons.TextFader.fade(self.dummy_dll_list,
                                "\ue8b7\nPlease select a game directory")
        tkaddons.TextFader.fade(self.gamename, '')
        self.info("Updating dlls done | Now we can speed up your system")

    @new_thread
    def _update_callback(self):
        self.update_button.config(state='disabled')
        self.restore_button.config(state='disabled')
        self.select_all_button.config(state='disabled')
        self.browse.config(state='disabled')
        self.dummy_dll_list.pack(expand=True)
        self.dll_listbox.pack_forget()
        tkaddons.TextFader.fade(self.dummy_dll_list,
                                "\ue896\nUpdating your dlls..")
        reminder.stop()

        dlls = self._get_dll_selection()
        DllUpdater.update_dlls(self.path, dlls)

        self.browse.config(state='normal')

        tkaddons.TextFader.fade(self.dummy_dll_list, "\ue930\nCompleted")

        self._reset_tab0()
        reminder.remind(self.tab2)

        @new_thread
        def system_tab_hook():
            self.wait_visibility(self.system)
            reminder.stop()

        system_tab_hook()

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

    def _listboxselection_callback(self):
        """Updates the Select all button automatically based on states of items of dll_listbox"""
        selectable = len([
            index for index in self.dll_listbox.curselection()
            if index not in self.dll_listbox.disabled
        ])

        selection = len(self.dll_listbox.curselection())

        if not selectable:
            self.select_all_button.config(state='disabled')
            return

        else:
            self.select_all_button.config(state='normal')

        if not selection:
            self.update_button.config(state='disabled')
            self.restore_button.config(state='disabled')

        else:
            self.update_button.config(state='normal')
            self.restore_button.config(state='normal')

    def _selectall_callback():
        selectable = len([
            index for index in self.dll_listbox.curselection()
            if index not in self.dll_listbox.disabled
        ])

        selection = len(self.dll_listbox.curselection())

        if selectable - selection > 0:
            self._select_all()
        else:
            self._deselect_all()

        self._listboxselection_callback()

    def _select_all(self):
        """Selects all items in dll_listbox"""
        self.commonpaths_listbox.unbind(
            "<<ListboxSelect>>"
        )  # -------------------------------------------------------------| - hotfix (probably tkinter library issue)
        self.dll_listbox.selection_set(  #                                |
            0, 'end')  #                                                  |
        self.commonpaths_listbox.bind(  #                                 |
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

        self._update_game_path(_path)

    def _ask_directory(self):
        return tk.filedialog.askdirectory(title="Select game directory")

    @new_thread
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

        try:
            self._disable_unavailable_dlls()

        except SyncError:
            self.info(
                "Error while syncing with GitHub | Is your connection ok? Please write us a support request"
            )
            tkaddons.TextFader.fade(window.dummy_dll_list,
                                    "\uEA6A\nSync error")
            self._reset_tab0()

        self._select_all()
        self._listboxselection_callback()

        self.dummy_dll_list.pack_forget()
        self.dll_listbox.config(
            bg=frm_cnf['bg'], highlightbackground=frm_cnf['bg'])
        self.dll_listbox.pack(fill='both')
        tkaddons.fade(
            self.dll_listbox,
            bg=listbox_cnf['bg'],
            highlightbackground=listbox_cnf['highlightbackground'])

        self.select_all_button.config(state='normal')
        tkaddons.TextFader.fade(self.gamename, self.path)
        tkaddons.TextFader.fade(self.available_updates_label,
                                "Available dll updates")
        self.update_button.config(state='normal')
        if DllUpdater.available_restore(path):
            self.restore_button.config(state='normal')
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
        available = DllUpdater.available_dlls()

        if available == []:
            raise SyncError

        for index, dll_name in enumerate(self.dll_listbox.get(0, 'end')):
            if dll_name not in available:
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

        INTERVAL = .04

        while True:
            for i in range(80):
                self.canvas.move("logo", 0, 5)
                self.canvas.update()
                sleep(INTERVAL)

            for i in range(160):
                self.canvas.move("logo", 5, 0)
                self.canvas.update()
                sleep(INTERVAL)

            for i in range(80):
                self.canvas.move("logo", 0, -5)
                self.canvas.update()
                sleep(INTERVAL)

            for i in range(160):
                self.canvas.move("logo", -5, 0)
                self.canvas.update()
                sleep(INTERVAL)

    @new_thread
    def tab_switch(self, id):
        """Displays a frame of given id on canvas"""
        id_frm = {
            'System': self.system,
            'Games': self.games,
            'Collection': self.collection_frame,
        }

        try:
            self.display_cont_frame(id_frm[id])

        except KeyError:
            dummy = self.FrameTab(self, self)
            dummy_lb = tk.Label(
                dummy, text="\ue822\nUnder construction..", **biglb_cnf)
            dummy_lb.pack(expand=True, fill='both')

            self.display_cont_frame(dummy)

        # Navigation bar configuration
        for wg in self.navigation.pack_slaves():
            if wg["text"] == id:
                wg.unbind("<Leave>")
                wg.unbind("<Enter>")
                tkaddons.fade(wg, btn_active)

            elif wg["text"] == self.active_tab:
                wg.bind(
                "<Enter>",
                lambda *args, wg=wg: tkaddons.fade(wg, btn_hover)
                )
                wg.bind(
                "<Leave>",
                lambda *args, wg=wg: tkaddons.fade(wg, btn)
                )
                tkaddons.fade(wg, btn)

        self.active_tab = id

    def _clickwin(self, event):
        """Prepares variables for _dragwin function"""
        self.offsetx = self.winfo_pointerx() - self.winfo_x()
        self.offsety = self.winfo_pointery() - self.winfo_y()

    def _dragwin(self, event):
        """Updates window position"""
        x = self.winfo_pointerx() - self.offsetx
        y = self.winfo_pointery() - self.offsety
        self.geometry('+%d+%d' % (x, y))


gui = NOP()

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

    gui = window

    start_new(window.logo_animation, ())
    start_new(window.tab_switch, (window.active_tab, ))

    root.mainloop()
