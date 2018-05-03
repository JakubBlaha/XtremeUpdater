from theme import *

btn = {
    'bg': DARK,
    'fg': FG,
    'relief': 'flat',
    'font': ('Roboto', 13),
    'cursor': 'hand2',
    'activebackground': DARK,
    'activeforeground': PRIM,
    'bd': 0,
}
btn_head = {**btn, 'width': 2, 'font': ('Roboto', 14), 'bg': DARK}
btn_hover = {**btn, 'fg': PRIM}
btn_active = {
    **btn,
    'bg': PRIM,
    'fg': DARK,
}
secbtn = {**btn, 'bg': DARK, 'fg': FG, 'font': ('Roboto', 11), 'bd': 0}

lb_cnf = {'bg': DARK, 'fg': FG, 'font': ('Roboto', 11)}
seclb_cnf = {'bg': DARK, 'fg': PRIM, 'font': ('Roboto', 8)}
biglb_cnf = {**lb_cnf, 'fg': PRIM, 'font': ('Segoe UI', 24)}
hlb_cnf = {
    'bg': DARK,
    'fg': PRIM,
    'font': ('Roboto', 11, 'bold'),
    'anchor': 'w'
}
wrnlb_cnf = {
    'bg': DARK,
    'fg': 'red',
    'font': ('Roboto Light', 9, 'bold'),
    'wraplength': 290
}
frm_cnf = {'bg': DARK, 'padx': 4, 'pady': 0}
lbfrm_cnf = {
    'bg': DARK,
    'padx': 4,
    'pady': 4,
    'fg': PRIM,
    'font': ('Roboto', 11, 'bold'),
    'bd': 0,
    'highlightbackground': PRIM,
    'highlightthickness': '1',
    'labelanchor': 'n'
}
cnv_cnf = {'highlightthickness': 0, 'bg': 'black'}
listbox_cnf = {
    'bg': SEC,
    'font': ('Roboto', 11),
    'fg': FG,
    'relief': 'flat',
    'selectbackground': PRIM,
    'selectmode': 'extended',
    'highlightthickness': 10,
    'highlightbackground': SEC,
    'highlightcolor': SEC,
    'activestyle': 'none',
    'cursor': 'hand2'
}

btn_nav_pck = {'side': 'left', 'ipadx': 10}
nav_frm_pck = {'side': 'top', 'anchor': 'w', 'fill': 'x', 'expand': True}
head_frm_pck = {'side': 'top', 'fill': 'x'}
title_lb_pck = {
    'side': 'left',
    'fill': 'both',
    'ipadx': 10,
    'ipady': 5,
    'expand': True
}
btn_head_pck = {'side': 'right', 'fill': 'y'}
cnv_pck = {'side': 'top'}
