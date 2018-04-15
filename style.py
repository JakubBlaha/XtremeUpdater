import tkinter as tk

from theme import *

btn_cnf = {
    "bg": DARK,
    "fg": FG,
    "relief": tk.FLAT,
    "font": ("Roboto", 13),
    "cursor": "hand2",
    "activebackground": DARK,
    "activeforeground": PRIM,
    "bd": 0,
}
btn_nav_cnf = {
    **btn_cnf,
    **{
        "font": ("Roboto", 14, "bold"),
    }
}
btn_head_cnf = {"width": 2, "font": ("Roboto", 14), "bg": DARK}
btn_normal_cnf_cfg = {"fg": FG, "bg": DARK}
btn_hover_cnf_cfg = {"fg": PRIM}
btn_normal_from_hover_cnf_cfg = {"fg": btn_normal_cnf_cfg["fg"]}
btn_active_cnf_cfg = {
    "bg": PRIM,
    "fg": FG,
}
lb_cnf = {"bg": DARK, "fg": FG, "font": ("Roboto", 11)}
seclb_cnf = {"bg": DARK, "fg": PRIM, "font": ("Roboto", 8)}
hlb_cnf = {"bg": DARK, "fg": FG, "font": ("Roboto", 11, "bold")}
wrnlb_cnf = {
    "bg": DARK,
    "fg": "red",
    "font": ("Roboto Light", 9, "bold"),
    "wraplength": 290
}
frm_cnf = {"bg": DARK, "padx": 4, "pady": 0}
cont_frm_cnf = {**frm_cnf, **{"pady": 4}}
nav_frm_cnf = {**frm_cnf, **{"padx": 0, "bg": DARK}}
lbfrm_cnf = {
    "bg": DARK,
    "padx": 4,
    "pady": 4,
    "fg": PRIM,
    "font": ("Roboto", 11, "bold"),
    "bd": 0,
    "highlightbackground": PRIM,
    "highlightthickness": "1",
    "labelanchor": "n"
}
cnv_cnf = {"highlightthickness": 0, "highlightbackground": "#10131a"}
listbox_cnf = {
    "bg": SEC,
    "font": ("Roboto", 11),
    "fg": FG,
    "relief": 'flat',
    "selectbackground": PRIM,
    "selectmode": 'extended',
    "highlightthickness": 10,
    "highlightbackground": SEC,
    "highlightcolor": SEC,
    "activestyle": "none",
    "cursor": "hand2"
}
scrollbar_cnf = {"troughcolor": DARK}

btn_nav_pck = {"side": tk.LEFT, "expand": True, "fill": tk.X}
nav_frm_pck = {"side": tk.TOP, "anchor": "w", "fill": tk.X, "expand": True}
head_frm_pck = {"side": tk.TOP, "fill": tk.X}
title_lb_pck = {"side": tk.LEFT, "fill": tk.BOTH, "expand": True}
logo_lb_pck = {"side": tk.LEFT}
btn_head_pck = {"side": tk.RIGHT, "fill": tk.Y}
cnv_pck = {"side": tk.TOP}
