from kivy import Config
from kivy.app import App
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.animation import Animation
from kivy.lang.builder import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty

Config.set('graphics', 'width', 300)
Config.set('graphics', 'height', 400)
Config.set('graphics', 'borderless', 1)

from kivy.core.window import Window

Builder.load_string(
'''
#:import theme theme
#:import resource_path resource_path.resource_path

<RootLayout@BoxLayout>:
    orientation: 'vertical'
    padding: 20, 30

    canvas:
        Color:
            rgba: theme.bg
        Rectangle:
            pos: self.pos
            size: self.size

    Image:
        canvas.before:
            PushMatrix
            Rotate:
                angle: root.logo_angle
                origin: self.center
        canvas.after:
            PopMatrix

        id: logo
        source: resource_path('icon_no_bg.png')
    Label:
        id: info
        text: 'Welcome to XtremeUpdater setup'
        size_hint_y: None
        height: 100
        markup: True
        halign: 'center'
        valign: 'top'
'''
)

import os
from theme import *
from _thread import start_new
from pygit2 import clone_repository
from win32com.client import Dispatch
from pythoncom import CoInitialize

REPO_URL = 'https://github.com/XtremeWare/XtremeUpdater-Distribution'
USR_PATH = os.path.expanduser('~')
PATH = USR_PATH + '\\AppData\\Local\\XtremeUpdater\\'
LAUNCHER_PATH = PATH + '\XtremeUpdater\launcher.exe'
START_PATH = USR_PATH + '\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\'
LNK_PATH = START_PATH + 'XtremeUpdater.lnk'

def clone():
    clone_repository(REPO_URL, PATH)

def make_lnk():
    CoInitialize()
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(LNK_PATH)
    shortcut.Targetpath = LAUNCHER_PATH
    shortcut.IconLocation = LAUNCHER_PATH
    shortcut.WorkingDirectory = os.path.dirname(LAUNCHER_PATH)
    shortcut.save()

def start():
    os.startfile(LNK_PATH)

def setup():
    app.info(f'Installing [color={PRIM}]XtremeUpdater[/color]')
    try:
        clone()
    except:
        app.error()
        return
    app.info('Adding shortcut')
    make_lnk()
    app.info('Starting the app')
    start()
    app.stop()

class RootLayout(BoxLayout):
    logo_angle = NumericProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        self.logo_rotate_clock = Clock.schedule_interval(self.logo_rotate, 1.5)

    def logo_rotate(self, *args):
        Animation(logo_angle=self.logo_angle + 360, d=1, t='in_out_expo').start(self)

    def error(self):
        self.logo_rotate_clock.cancel()
        self.info(f'[color=f00]Could not install[/color]\n\n[color={PRIM}][u][ref=support]Support[/ref][/u], [u][ref=close]Close[/ref][/u][/color]')
        self.ids.info.bind(on_ref_press=self.ref_press)

        Animation(opacity=0, d=.5, t='out_expo').start(self.ids.logo)
        Animation(size=[300, 150], d=.5, t='out_expo').start(Window)

    def ref_press(self, _, name):
        if name == 'support':
            os.startfile('https://discord.gg/Cs4rstF')
        elif name == 'close':
            app.close()
    
    def info(self, text):
        self.ids.info.text = text


class SetupApp(App):
    def build(self):
        return RootLayout()

    def info(self, *args):
        self.root.info(*args)

    def error(self):
        self.root.error()
    
    def on_start(self):
        start_new(setup, ())

    def close(self):
        anim = Animation(size=[300, 1], d=.5, t='out_expo')
        anim.bind(on_complete=self.stop)
        anim.start(Window)

if __name__ == '__main__':
    app = SetupApp()
    app.run()