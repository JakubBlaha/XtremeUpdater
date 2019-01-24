from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.animation import Animation
from kivy.lang.builder import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty
from resource_path import resource_path

from kivy import Config
Config.set('graphics', 'width', 300)
Config.set('graphics', 'height', 400)
Config.set('graphics', 'borderless', 1)
Config.set('graphics', 'resizable', 0)
Config.set('kivy', 'window_icon', 'icon_no_bg.png')
import os
LOGS_PATH = os.getcwd() + r'\XUI_logs'
Config.set('kivy', 'log_dir', LOGS_PATH)

from kivy.core.window import Window

Builder.load_string('''
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
            source: resource_path('noise.png')

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
        size_hint_y: None
        height: 100
        markup: True
        halign: 'center'
        valign: 'top'
''')

import traceback
from theme import *
from _thread import start_new
from urllib.request import urlretrieve
from pythoncom import CoInitialize
from pygit2 import clone_repository
from win32com.client import Dispatch
import shutil
import subprocess

REPO_URL = 'https://github.com/XtremeWare/XtremeUpdater-Distribution'
LAUNCHER_URL = r'https://github.com/XtremeWare/XtremeUpdater/raw/master/utils/XtremeUpdater%20Launcher/launcher/launcher.exe'
USR_PATH = os.path.expanduser('~')
PATH = USR_PATH + '\\AppData\\Local\\XtremeUpdater\\'
REPO_PATH = PATH + 'repo'
LAUNCHER_PATH = PATH + 'launcher.exe'
START_PATH = USR_PATH + '\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\'
LNK_PATH = START_PATH + 'XtremeUpdater.lnk'


def clear_installation_dir():
    ''' Removes the installation directory. Return `True` if success. '''
    try:
        subprocess.Popen(
            ['powershell.exe', f'Remove-Item {PATH} -Force -Recurse'])
    except Exception:
        Logger.error(f'ClearDir: {traceback.format_exc()}')
        return False
    return True


def clone():
    clone_repository(REPO_URL, REPO_PATH)


def download_launcher():
    urlretrieve(LAUNCHER_URL, LAUNCHER_PATH)


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
    try:
        os.makedirs(REPO_PATH, exist_ok=True)
    except PermissionError:
        pass

    app.info(f'Installing [color={PRIM}]XtremeUpdater[/color]')
    try:
        clone()
    except Exception:
        Logger.error(traceback.format_exc())
        app.root.already_installed()
        return

    app.info('Downloading launcher')
    try:
        download_launcher()

    except ValueError:
        app.error()

    except Exception:
        Logger.error(traceback.format_exc())
        app.error()
        return

    app.info('Adding shortcut')
    try:
        make_lnk()
    except Exception:
        Logger.error(traceback.format_exc())
        app.error()
        return

    app.info('Starting the app')
    try:
        start()
    except Exception:
        Logger.error(traceback.format_exc())
        app.error()
        return

    app.stop()


class RootLayout(BoxLayout):
    logo_angle = NumericProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        self.ids.info.bind(on_ref_press=self.ref_press)
        self.begin_logo_rotation()

    def begin_logo_rotation(self):
        self.logo_rotate_clock = Clock.schedule_interval(self.logo_rotate, 1.5)

    def logo_rotate(self, *args):
        Animation(
            logo_angle=self.logo_angle + 360, d=1, t='in_out_expo').start(self)

    def error(self):
        self.logo_rotate_clock.cancel()
        self.info(
            f'[color=f55]Could not install[/color]\n\n[color={PRIM}][u][ref=support]Support[/ref][/u], [u][ref=close]Close[/ref][/u], [u][ref=logs]Logs[/ref][/u][/color]'
        )

        self.logo_visible(False)

    def logo_visible(self, visible):
        Animation(opacity=visible, d=.5, t='out_expo').start(self.ids.logo)
        Animation(
            size=[300, 400] if visible else [300, 150], d=.5,
            t='out_expo').start(Window)

    def already_installed(self):
        self.logo_rotate_clock.cancel()
        self.info(
            f'[color=f55]Directory already exists[/color]\n\n[color={PRIM}][u][ref=overwrite_dir]Overwrite directory[/ref][/u][/color]'
        )

        self.logo_visible(False)

    def ref_press(self, _, ref):
        if ref == 'support':
            os.startfile('https://discord.gg/Cs4rstF')
        elif ref == 'close':
            app.close()
        elif ref == 'logs':
            os.startfile(LOGS_PATH)
        elif ref == 'overwrite_dir':
            ret = clear_installation_dir()
            if ret:
                self.logo_visible(True)
                self.begin_logo_rotation()
                start_new(setup, ())
            else:
                app.info(
                    '[color=f55]Failed to remove the directory[/color]\n\nPlese do it manually'
                )

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
        Animation(size=[300, 1], d=.5, t='out_expo').start(Window)
        Clock.schedule_once(self.stop, .3)


if __name__ == '__main__':
    app = SetupApp()
    app.run()
