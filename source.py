import tkinter as tk
import tkinter.filedialog
from tkinter import ttk
import os
from time import sleep
from _thread import start_new

from theme import *
from style import *
from cw import center_window
from resources import *
import wgmethods
import customfont


class DllUpdater:
    available_dlls = (
        'D3DCompiler_47.dll', 'D3DX9_43.dll', 'NPSWF32.dll',
        'api-ms-win-core-console-l1-1-0.dll',
        'api-ms-win-core-datetime-l1-1-0.dll',
        'api-ms-win-core-debug-l1-1-0.dll',
        'api-ms-win-core-errorhandling-l1-1-0.dll',
        'api-ms-win-core-file-l1-1-0.dll', 'api-ms-win-core-file-l1-2-0.dll',
        'api-ms-win-core-file-l2-1-0.dll', 'api-ms-win-core-handle-l1-1-0.dll',
        'api-ms-win-core-heap-l1-1-0.dll',
        'api-ms-win-core-interlocked-l1-1-0.dll',
        'api-ms-win-core-libraryloader-l1-1-0.dll',
        'api-ms-win-core-localization-l1-2-0.dll',
        'api-ms-win-core-memory-l1-1-0.dll',
        'api-ms-win-core-namedpipe-l1-1-0.dll',
        'api-ms-win-core-processenvironment-l1-1-0.dll',
        'api-ms-win-core-processthreads-l1-1-0.dll',
        'api-ms-win-core-processthreads-l1-1-1.dll',
        'api-ms-win-core-profile-l1-1-0.dll',
        'api-ms-win-core-rtlsupport-l1-1-0.dll',
        'api-ms-win-core-string-l1-1-0.dll',
        'api-ms-win-core-synch-l1-1-0.dll', 'api-ms-win-core-synch-l1-2-0.dll',
        'api-ms-win-core-sysinfo-l1-1-0.dll',
        'api-ms-win-core-timezone-l1-1-0.dll',
        'api-ms-win-core-util-l1-1-0.dll', 'api-ms-win-crt-conio-l1-1-0.dll',
        'api-ms-win-crt-convert-l1-1-0.dll',
        'api-ms-win-crt-environment-l1-1-0.dll',
        'api-ms-win-crt-filesystem-l1-1-0.dll',
        'api-ms-win-crt-heap-l1-1-0.dll', 'api-ms-win-crt-locale-l1-1-0.dll',
        'api-ms-win-crt-math-l1-1-0.dll',
        'api-ms-win-crt-multibyte-l1-1-0.dll',
        'api-ms-win-crt-private-l1-1-0.dll',
        'api-ms-win-crt-process-l1-1-0.dll',
        'api-ms-win-crt-runtime-l1-1-0.dll', 'api-ms-win-crt-stdio-l1-1-0.dll',
        'api-ms-win-crt-string-l1-1-0.dll', 'api-ms-win-crt-time-l1-1-0.dll',
        'api-ms-win-crt-utility-l1-1-0.dll', 'cg.dll', 'cgD3D9.dll',
        'cgGL.dll', 'concrt140.dll', 'd3dx11_43.dll', 'msvcp140.dll',
        'tbb.dll', 'tbbmalloc.dll', 'ucrtbase.dll', 'vccorlib140.dll',
        'vcomp120.dll', 'vcomp140.dll', 'vcruntime140.dll')


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
        self.flash_browse_button = True
        self.last_listbox_item_highlight = 0

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
            text="...",
            command=self.__update_game_path,
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
            command=self.__select_all,
            **btn_cnf)
        self.dll_listbox = tk.Listbox(
            self.dll_frame, width=90, height=16, **listbox_cnf)
        self.listbox_scrollbar = ttk.Scrollbar(
            self.dll_frame, command=self.dll_listbox.yview)
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
        # self.listbox_scrollbar.pack(side='left', fill='y')
        # system frame
        self.spectre_patch_lbframe.pack(anchor="w")
        self.spectrewrn_label.pack()
        self.spectre_patch_disable.pack()
        self.spectre_patch_enable.pack()

        self.__bind_wgs()

        self.canvas_setup()
        start_new(self.__browse_button_remind_loop, ())

        self.__update_dll_listbox(["Hello", "world", "spam", "egg", "!!!"])

        self.__update_select_button()

    def __update_listbox_item_height(self):
        self.listbox_item_height_px = (self.dll_frame.winfo_height() -
                                       self.dll_frame["highlightthickness"] * 2
                                       ) // self.dll_listbox["height"]

    def __listbox_hover_item_update(self, event):
        if not 'self.listbox_item_height_px' in locals():
            self.__update_listbox_item_height()

        new_listbox_item_highlight = event.y // self.listbox_item_height_px + self.dll_listbox.nearest(
            0) + ((-4 if event.delta > 0 else 4) if event.delta != 0 else 0)
        if new_listbox_item_highlight + 1 > self.dll_listbox.size(): return
        # wgmethods.fade_listbox_item(self.dll_listbox,
        #                             self.last_listbox_item_highlight,
        #                             "foreground", FG)
        self.dll_listbox.itemconfig(self.last_listbox_item_highlight, fg=FG)
        if self.dll_listbox.itemcget(new_listbox_item_highlight, "fg") != BG:
            # wgmethods.fade_listbox_item(self.dll_listbox,
            #                             new_listbox_item_highlight,
            #                             "foreground", PRIM)
            self.dll_listbox.itemconfig(new_listbox_item_highlight, fg=PRIM)
            self.last_listbox_item_highlight = new_listbox_item_highlight

    def __update_select_button(self):
        """Updates the Select all button automatically based on states of items of dll_listbox"""
        selectable = 0
        for i in range(self.dll_listbox.size()):
            if self.dll_listbox.itemcget(i, 'fg') != DISABLED:
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
                command=self.__deselect_all,
                state='normal')
        else:
            self.select_all_button.config(
                text="Select all", command=self.__select_all, state='normal')

    def __select_all(self):
        """Selects all items in dll_listbox"""
        self.dll_listbox.selection_set(0, 'end')
        self.select_all_button.config(
            text="Deselect all", command=self.__deselect_all)

    def __deselect_all(self):
        """Deselects all items in dll_listbox"""
        self.dll_listbox.selection_clear(0, 'end')
        self.select_all_button.config(
            text="Select all", command=self.__select_all)

    def __browse_button_remind_loop(self):
        """Creates an fading animation on the browse_button reminding the user of selecting a directory"""
        sleep(2)
        while self.flash_browse_button:
            wgmethods.fade(self.browse_button, 'bg', PRIM, 50)
            sleep(1)
            wgmethods.fade(self.browse_button, 'bg', DARK, 10)
            sleep(1)

    def __update_game_path(self):
        """Asks user for a game path and updates everything tied together with it"""
        self.flash_browse_button = False

        path = tk.filedialog.askdirectory(title="Select game directory")

        ext = ".dll"
        dll_names = [
            name for name in os.listdir(path)
            if os.path.splitext(name)[1] == ext
        ]

        self.__update_dll_listbox(dll_names)
        self.__update_select_button()

        self.selected_game_label.config(text=os.path.basename(path))

    def __update_dll_listbox(self, dll_names):
        """Overwrites dll_listbox items with new ones given in the dll_names parameter"""
        self.dll_listbox.delete(0, 'end')
        for dll_name in dll_names:
            self.dll_listbox.insert('end', dll_name)
            if dll_name not in DllUpdater.available_dlls:
                self.dll_listbox.itemconfig(
                    dll_names.index(dll_name),
                    foreground=BG,
                    background=SEC,
                    selectforeground=BG,
                    selectbackground=SEC)
            else:
                self.dll_listbox.itemconfig(
                    dll_names.index(dll_name),
                    foreground=FG,
                    background=SEC,
                    selectforeground=FG,
                    selectbackground=PRIM)
        self.__select_all()

    def __remove_content_frame(self):
        self.cont_canvas.delete(self.cont_frm_id)

    def display_cont_frame(self, frame):
        # This function overwrites frame content frame currently disaplayed on the canvas, frame attribute represents a tk.Frame instance which will be displayed on the canvas
        self.__remove_content_frame()
        self.cont_frm_id = self.cont_canvas.create_window(
            (10, 10),
            window=frame,
            anchor="nw",
            width=self.cont_canvas.winfo_width() - 20,
            height=self.cont_canvas.winfo_height() - 20)

    def logo_animation(self):
        # This function creates logo animation
        for i in range(50):
            self.cont_canvas.move("logo", -1, -1)
            self.cont_canvas.update()
            sleep(i / 1000)

    def tab_switch(self, id):
        # Content display
        id_frm = {"System": self.system_frame, "Games": self.games_frame}

        try:
            self.display_cont_frame(id_frm[id])

        except KeyError:
            self.__remove_content_frame()

        # Navigation bar animations and configurations
        for btn in self.nav_frame.pack_slaves():
            if btn["text"] == id:
                btn.unbind("<Leave>")
                btn.unbind("<Enter>")
                wgmethods.fade(btn, tuple(btn_active_cnf_cfg.keys()),
                               tuple(btn_active_cnf_cfg.values()))

            elif btn["text"] == self.active_tab:
                btn.bind(
                "<Enter>",
                lambda *args, btn=btn: wgmethods.fade(btn, tuple(btn_hover_cnf_cfg.keys()), tuple(btn_hover_cnf_cfg.values()))
                )
                btn.bind(
                "<Leave>",
                lambda *args, btn=btn: wgmethods.fade(btn, tuple(btn_normal_cnf_cfg.keys()), tuple(btn_normal_cnf_cfg.values()))
                )
                wgmethods.fade(btn, tuple(btn_normal_cnf_cfg.keys()),
                               tuple(btn_normal_cnf_cfg.values()))

        self.active_tab = id

    def canvas_setup(self):
        # This function prepares always on canvas items
        self.ximage = self.cont_canvas.create_image(
            -40,
            -40,
            image=get_img("img/acrylic_dark.png"),
            anchor="nw",
            tags="logo")

    def __bind_wgs(self):
        # This function binds on-hover actions and makes window to be moveable by the user
        self.btns = (self.games_button, self.chat_button, self.system_button,
                     self.minimize_button, self.close_button,
                     self.browse_button)
        for btn in self.btns:
            btn.bind(
                "<Enter>",
                lambda *args, btn=btn: wgmethods.fade(btn, tuple(btn_hover_cnf_cfg.keys()), tuple(btn_hover_cnf_cfg.values()))
            )
            btn.bind(
                "<Leave>",
                lambda *args, btn=btn: wgmethods.fade(btn, tuple(btn_normal_from_hover_cnf_cfg.keys()), tuple(btn_normal_cnf_cfg.values()))
            )

        self.title_label.bind("<Button-1>", self.__clickwin)
        self.title_label.bind("<B1-Motion>", self.__dragwin)

        self.spectrewrn_label.bind(
            "<Button-3>", lambda *args: self.spectrewrn_label.pack_forget())
        # self.dll_frame.bind("<Enter>", lambda *args: self.listbox_scrollbar.pack(side='left', fill='y'))
        self.dll_frame.bind("<Leave>",
                            lambda *args: self.listbox_scrollbar.pack_forget())
        self.dll_listbox.bind("<<ListboxSelect>>",
                              lambda *args: self.__update_select_button())
        self.dll_listbox.bind("<Motion>", self.__listbox_hover_item_update)
        self.dll_listbox.bind("<MouseWheel>", self.__listbox_hover_item_update)

    def __clickwin(self, event):
        # This function is called when user clicks window-head in order to move the window, it prepares variables for dragwin function
        self.offsetx = self.winfo_pointerx() - self.winfo_x()
        self.offsety = self.winfo_pointery() - self.winfo_y()

    def __dragwin(self, event):
        # This function is called when user tries to move the window-head, it woves the window to new position
        x = self.winfo_pointerx() - self.offsetx
        y = self.winfo_pointery() - self.offsety
        self.geometry('+%d+%d' % (x, y))


customfont.loadfont(resource_path("fnt/Roboto-Regular.ttf"))
customfont.loadfont(resource_path("fnt/Roboto-Light.ttf"))

root = Root()
start_new(root.top.logo_animation, ())
start_new(root.top.tab_switch, (root.top.active_tab, ))
root.top.tab_switch(root.top.active_tab)

root.mainloop()