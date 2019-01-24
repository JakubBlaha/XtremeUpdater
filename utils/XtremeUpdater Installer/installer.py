import yaml
import os
import pythoncom
import win32com.client
import traceback
from urllib.request import urlopen, URLError
from collections import defaultdict, OrderedDict
from pygit2 import (Repository, clone_repository, discover_repository,
                    RemoteCallbacks, GIT_RESET_HARD, GitError)
from _thread import start_new

from kivy import Config
LOGS_PATH = os.getcwd() + r'\XUI_logs'
Config.set('kivy', 'log_dir', LOGS_PATH)
Config.set('graphics', 'width', 1020)
Config.set('graphics', 'height', 570)
Config.set('graphics', 'borderless', True)
Config.set('graphics', 'resizable', False)
Config.set('graphics', 'maxfps', 60)
Config.set('input', 'mouse', 'mouse, disable_multitouch')
Config.set('kivy', 'window_icon', 'img/icon.ico')

from kivy.resources import resource_add_path
from kivy.app import App
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.logger import Logger
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.properties import (NumericProperty, ListProperty, StringProperty,
                             BooleanProperty, ObjectProperty)
from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label

from resource_path import resource_path

# CONSTANTS
REPO_URL = 'https://github.com/XtremeWare/XtremeUpdater-Distribution'
USR = os.path.expanduser('~')
LOCAL_APPDATA = os.getenv('LOCALAPPDATA')
APPDATA = os.getenv('APPDATA')
LOCAL_REPO_PATH = os.path.join(USR, LOCAL_APPDATA, 'XtremeUpdater')
START_MENU_PATH = os.path.join(APPDATA,
                               'Microsoft/Windows/Start Menu/Programs')
LNK_PATH = os.path.join(START_MENU_PATH, 'XtremeUpdater.lnk')
EXE_PATH = os.path.join(LOCAL_REPO_PATH, 'XtremeUpdater/Xtreme.exe')


# INSTALLER
class Installer:
    @staticmethod
    def discover_repository() -> bool:
        return bool(discover_repository(LOCAL_REPO_PATH))

    @staticmethod
    def is_dir_occupied() -> bool:
        ''' Whether installation dir is available. '''
        if not os.path.isdir(LOCAL_REPO_PATH):
            return False
        return bool(os.listdir(LOCAL_REPO_PATH))

    @staticmethod
    def clear_dir() -> bool:
        ''' Empties installation dir. Return whether success. '''
        try:
            os.system('powershell.exe '
                      f'Remove-Item {LOCAL_REPO_PATH} -Force -Recurse')
        except Exception:
            Logger.error(f'ClearDir: {traceback.format_exc()}')
            return False
        return True

    @staticmethod
    def create_dir():
        ''' Created the installation directory. '''
        try:
            os.makedirs(LOCAL_REPO_PATH, exist_ok=True)
        except Exception:
            Logger.error(f'mkdir: {traceback.format_exc()}')
            return False
        return True

    @staticmethod
    def clone():
        ''' Clones the actual distribution repository. '''
        try:
            clone_repository(
                REPO_URL,
                LOCAL_REPO_PATH,
                callbacks=ProgressBarCallback(
                    App.get_running_app().root.ids.progressbar))
        except ValueError:
            Logger.error(f'clone: {traceback.format_exc()}')
            return False
        except Exception:
            Logger.error(f'clone: {traceback.format_exc()}')
            return False
        return True

    @classmethod
    def fetch(cls):
        # Note that fetch does not produce output on the progressbar
        cls._repo = Repository(LOCAL_REPO_PATH)
        try:
            cls._repo.remotes['origin'].fetch(callbacks=ProgressBarCallback(
                    App.get_running_app().root.ids.progressbar))
        except Exception:
            return False
        return True

    @classmethod
    def reset(cls):
        try:
            cls._repo.reset(
                cls._repo.lookup_reference('refs/remotes/origin/master').
                get_object().oid, GIT_RESET_HARD)
        except GitError:
            return False
        return True

    @staticmethod
    def create_lnk():
        ''' Creates a `.lnk` file for the windows start menu. '''
        pythoncom.CoInitialize()
        shell = win32com.client.Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(LNK_PATH)
        shortcut.Targetpath = EXE_PATH
        shortcut.IconLocation = EXE_PATH
        shortcut.WorkingDirectory = os.path.dirname(EXE_PATH)
        shortcut.save()

        return True

    @staticmethod
    def start():
        ''' Starts the actual application after installed. '''
        try:
            return not os.startfile(EXE_PATH)
        except FileNotFoundError:
            return False

    @classmethod
    def full_install(cls):
        # Number of yields has to be static, needs to be iterated!
        _discovered = cls.discover_repository()
        yield True

        if _discovered:
            yield True
            yield True
            yield True

        else:
            yield cls.clear_dir() if cls.is_dir_occupied() else True

            yield cls.create_dir()

            yield cls.clone()

        yield cls.fetch()

        yield cls.reset()

        yield cls.create_lnk()

        yield cls.start()


# GIT
class ProgressBarCallback(RemoteCallbacks):
    progressbar = None

    def __init__(cls, progressbar):
        '''
        `progressbar` parameter should be an instance of `CustProgressBar`
        class. '''

        super().__init__()

        cls.progressbar = progressbar

    def transfer_progress(cls, progress):
        normal = progress.received_objects / progress.total_objects
        cls.progressbar.normal = normal
        Logger.info(f'TransferProgress: {normal}')

        return super().transfer_progress(progress)


# THEME
class ThemeMeta(type):
    THEME_URL = ('https://raw.githubusercontent.com/XtremeWare/XtremeUpdater-D'
                 'istribution/master/XtremeUpdater/theme/default.yaml')

    def __init__(cls, *args):
        super().__init__(*args)

        # Retrieve theme file
        try:
            _theme_data = urlopen(cls.THEME_URL).read()
        except URLError:
            cls._theme_dict = defaultdict((0, 1, 0, .5))
            Logger.error(
                f'Theme: Failed to access the theme file from address {cls.THEME_URL}'
            )
        else:
            cls._theme_dict = yaml.safe_load(_theme_data)['default']
            Logger.info(
                f'Theme: Retrieved theme file from {cls.THEME_URL} with values {cls._theme_dict}'
            )

    def __getattr__(cls, name):
        return get_color_from_hex(cls._theme_dict[name])

    def hex(cls, name):
        ''' Return the color but in hex. '''
        return cls._theme_dict[name]


class Theme(metaclass=ThemeMeta):
    pass


# UIX
class CustProgressBar(Widget):
    normal = NumericProperty()
    ''' A value representing the progress in range from `0` to `1`. '''

    color = ListProperty((1, 1, 1, 1))
    ''' The color of the line. '''

    background_color = ListProperty((0, 0, 0, 1))
    ''' The color of the ghost line. '''

    padding_x = NumericProperty()
    ''' The line x padding. '''

    # Internal use
    _px = NumericProperty()
    _normal = NumericProperty()
    _normal_anim = Animation()

    def on_normal(cls, __, normal):
        cls._normal_anim.cancel(cls)
        cls._normal_anim = Animation(_normal=normal, d=1, t='out_expo')
        cls._normal_anim.start(cls)


class CustButton(ButtonBehavior, Label):
    background_color = ListProperty((0, 0, 0, 0))
    background_hovering_color = ListProperty((0, 0, 0, 0))

    # Internal use
    _hovering = BooleanProperty(False)
    _background_color = ListProperty(Theme.bg)

    def __init__(cls, **kw):
        super().__init__(**kw)

        Window.bind(
            mouse_pos=
            lambda __, pos: setattr(cls, '_hovering', cls.collide_point(*pos))
        )

    def on__hovering(cls, __, is_hovering):
        if cls.disabled and is_hovering:
            return

        Animation(
            _background_color=cls.background_hovering_color
            if is_hovering else cls.background_color,
            d=.1).start(cls)
        Window.set_system_cursor('hand' if is_hovering else 'arrow')


class TodoList(GridLayout):
    items = ObjectProperty(OrderedDict())
    ''' A dictionary `item: status`, item is a string status bool. '''

    # Internal use
    _COLORS = {
        True: (.3, 1, .3, 1),
        False: (1, .3, .3, 1),
        None: Theme.sec,
        -1: Theme.fg
    }
    _last_items = OrderedDict()

    def on_items(cls, *__):
        cls.reload()

    def reload(cls):
        cls.clear_widgets()

        cls.rows = len(cls.items)
        for index, (key, value) in enumerate(cls.items.items()):
            # prepare color for smoother animation
            _old_value = cls._last_items.get(key)
            if _old_value == value:
                _init_color = cls._COLORS[value]
            elif _old_value == None:
                _init_color = Theme.sec
            else:
                _init_color = Theme.fg

            lb = Factory.TodoLabel(text='\u2022 ' + key, color=_init_color)

            if _old_value != value:
                Animation(color=cls._COLORS[value], d=.2).start(lb)

            cls.add_widget(lb)

        cls._last_items = OrderedDict(cls.items)


# ROOT
class Root(BoxLayout):
    pass


class InstallerApp(App):
    status = StringProperty(
        'By hitting the [i]Install[/i] button you agree to delete all '
        f'contents of [b]{LOCAL_REPO_PATH}[/b] if it exists.')
    install_progress = NumericProperty()
    error = BooleanProperty(False)
    progress_items = OrderedDict({
        'Discover local repository':
        None,
        'Clean the installation directory':
        None,
        'Create the installation directory':
        None,
        'Clone the remote distribution repository':
        None,
        'Fetch the local repository':
        None,
        'Reset the local repository':
        None,
        'Add a shortcut':
        None,
        'Start the app':
        None
    })
    PROGRESS_MESSAGES = [
        'Using a magnifying glass to find the local repository..',
        'Training the installation directory..',
        'Creativiting the installation directory..',
        'Trying to bait the repository down off the cloud..',
        'Trying to get an attention from the remote origin..',
        'Hardly trying to reset the local repository..',
        'Creating a lovely shortcut..', 'Waking up XtremeUpdater..'
    ]

    def __init__(cls, *args, **kw):
        super().__init__(*args, **kw)

        cls.Theme = Theme

        # animate window
        def on_frame(__):
            _height = Window.height
            Window.size = Window.width, 1
            Animation(
                size=[Window.width, _height], d=1, t='out_expo').start(Window)

        Clock.schedule_once(on_frame)

    def install(cls):
        cls.error = False
        cls.root.ids.install_btn.disabled = True
        cls.root.ids.progressbar.normal = 0
        Animation(color=Theme.prim, d=.5).start(cls.root.ids.progressbar)
        for key in cls.progress_items.keys():
            cls.progress_items[key] = None

        start_new(cls._install, ())

    def _install(cls):
        success = True
        keys = tuple(cls.progress_items.keys())
        for index, ret in enumerate(Installer.full_install()):
            _last = index == len(keys) - 1

            # white text
            if ret and not _last:
                cls.progress_items[keys[index + 1]] = -1
                cls.status = cls.PROGRESS_MESSAGES[index + 1]
            # colored text
            cls.progress_items[keys[index]] = ret
            # reload todo-list
            cls.root.ids.todo.items = cls.progress_items
            cls.root.ids.todo.reload()
            # error
            if not ret:
                success = False
                cls.root.ids.install_btn.disabled = False
                cls.error = True
                cls.status = ("I'm sorry.. I was not a good boy this time. "
                               'An error occured, please contact our support.')
                break

        # Animate progressbar
        Animation(
            color=((not success) * .7 + .3, success * .7 + .3, .3, 1),
            d=.5).start(cls.root.ids.progressbar)
        cls.root.ids.progressbar.normal = 1
        if success:
            cls.status = 'You can now use [i]XtremeUpdater[/i]. Nice!'


if __name__ == '__main__':
    resource_add_path(resource_path())
    Window.clearcolor = Theme.dark
    InstallerApp().run()