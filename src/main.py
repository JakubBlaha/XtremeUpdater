__version__ = '0.7.3'

import easygui
import yaml
import os
import sys
import win32api
import shutil
import ctypes
from random import randint
from _thread import start_new
from traceback import format_exc
from PIL import ImageFilter, Image
import platform
from io import BytesIO

import kivy
kivy.require('1.10.1')

from kivy import Config as KivyConfig
KivyConfig.set('graphics', 'width', 1000)
KivyConfig.set('graphics', 'height', 550)
KivyConfig.set('graphics', 'borderless', 1)
KivyConfig.set('graphics', 'resizable', 0)
KivyConfig.set('graphics', 'multisamples', 0)
KivyConfig.set('graphics', 'maxfps', 60)
KivyConfig.set('input', 'mouse', 'mouse, disable_multitouch')
KivyConfig.set('kivy', 'window_icon', 'img/icon.ico')
KivyConfig.set('kivy', 'log_dir', os.getcwd() + '/logs')

from kivy.app import App
from kivy.logger import Logger
from kivy.factory import Factory
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.clock import Clock, mainthread
from kivy.storage.jsonstore import JsonStore
from kivy.network.urlrequest import UrlRequest

from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.image import CoreImage
from kivy.uix.spinner import Spinner
from custpagelayout import PageLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView
from kivy.graphics.texture import Texture
from scrollview import ScrollView as SmoothScrollView
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.graphics import Rectangle, Color, Rotate, PushMatrix, PopMatrix, Fbo, Translate, Scale
from kivy.uix.label import Label, CoreLabel
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty, ObjectProperty, DictProperty, ListProperty, NumericProperty, BooleanProperty
from kivy.event import EventDispatcher
from kivy.metrics import sp

# custom uix
from uix.notifications import Notification, WorkingNotif
from uix.button import CustButton

from hovering import HoveringBehavior
from windowdragbehavior import WindowDragBehavior
from theme import Theme
from config import Config
Config.reload_store()
from dll_updater import DllUpdater
from fontcolor import font_color
from get_image_url import get_image_url_from_response, TEMPLATE, HEADERS
from cropped_thumbnail import cropped_thumbnail
from update_client import UpdateClient

IS_ADMIN = ctypes.windll.shell32.IsUserAnAdmin()


def new_thread(fn):
    def wrapper(*args, **kwargs):
        start_new(fn, args, kwargs)

    return wrapper


def silent_exc(fn):
    def wrapper(*args, **kw):
        app = App.get_running_app()

        try:
            fn(*args, **kw)
        except Exception:
            app.root.bar.error_ping()
        else:
            app.root.bar.ping()

    return wrapper


def notify_restart(fn):
    def wrapper(*args, **kw):
        fn(*args, **kw)
        Factory.Notification(
            title_='Restart system',
            message=
            f'This [color={theme.PRIM}]tweak[/color] may not work until the system is [color={theme.PRIM}]restarted[/color].'
        ).open()

    return wrapper


def refer_func(fn):
    '''
    Passes the function as an argument to the function itself. Can be used for
    referring itself.
    '''

    def wrapper(*args, **kw):
        return fn(fn, *args, **kw)

    return wrapper


class CustTextInput(TextInput):
    pass


class PathInput(CustTextInput):
    def on_focus(self, __, has_focus):
        if has_focus:
            self.update_color()
        else:
            self.foreground_color = theme.sec

    def on_text(self, *args):
        if self.focus:
            self.update_color()

    def update_color(self):
        GREEN, RED = (.3, 1, .3, 1), (1, .3, .3, 1)
        self.foreground_color = GREEN if os.path.isdir(
            os.path.abspath(self.text)) else RED


class Animation(Animation):
    def __init__(self, **kw):
        super().__init__(**kw)
        try:
            self._duration *= Config.get('animations', True)
        except (NameError, AttributeError):
            pass


class NoiseTexture(Widget):
    noise_color = ListProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        Clock.schedule_once(
            lambda *args: Clock.schedule_once(self.update_texture))

    def update_texture(self, *args):
        tex = CoreImage('img/noise_texture.png').texture
        tex.wrap = 'repeat'
        tex.uvsize = self.width / tex.width, self.height / tex.height

        self.canvas.before.clear()
        with self.canvas.before:
            if self.noise_color:
                Color(rgba=self.noise_color)
            Rectangle(pos=self.pos, size=self.size, texture=tex)

    def on_pos(self, *args):
        self.update_texture()

    def on_size(self, *args):
        self.update_texture()

    def on_noise_color(self, *args):
        self.update_texture()


class HeaderLabel(Label, WindowDragBehavior, NoiseTexture):
    current_icon = StringProperty('\ue78b')
    decors = []
    decor_rotations = []
    decor_enabled = BooleanProperty(False)

    def __init__(self, **kw):
        super().__init__(**kw)

        self.decor_enabled = Config.get('head_decor', True)

        if self.decor_enabled:
            Clock.schedule_once(
                lambda *args: Clock.schedule_once(self.setup_decor))

            if Config.get('animations', True):
                Clock.schedule_once(lambda *args: Clock.schedule_interval(self.random_decor_rotation, .5))

    def on_decor_enabled(self, __, value):
        Config.head_decor = value

        if value:
            self.setup_decor()
        else:
            self.clear_decor()

    def random_decor_rotation(self, *args):
        if not self.decor_rotations:
            return

        rotation = self.decor_rotations[randint(0,
                                                len(self.decor_rotations) - 1)]
        angle_add = randint(100, 200) * (1 - 2 * randint(0, 1))
        self.rotate_rotation(rotation, angle_add)

    def all_decor_rotation(self, *args):
        for rotation in self.decor_rotations:
            angle_add = 100 * (1 - 2 * randint(0, 1))
            self.rotate_rotation(rotation, angle_add)

    def rotate_rotation(self, rotation, angle_add):
        Animation(
            angle=rotation.angle + angle_add, d=.5,
            t='out_expo').start(rotation)

    def setup_decor(self, *args):
        X_OFFSET = 130
        WIDTH, HEIGHT = 20, 21
        SIZE = WIDTH, HEIGHT
        with self.canvas:
            for i in range(int(self.width - X_OFFSET) // WIDTH):
                rect_pos = (i * 48 + X_OFFSET, self.y + i % 2 * 10)
                rect_center = rect_pos[0] + WIDTH / 2, rect_pos[1] + HEIGHT / 2

                PushMatrix(group='decor')
                self.decor_rotations.append(
                    Rotate(
                        angle=randint(0, 360),
                        origin=rect_center,
                        group='decor'))
                self.decors.append(
                    Rectangle(pos=rect_pos, size=SIZE, group='decor'))
                PopMatrix(group='decor')

        self.on_current_icon()

    def on_current_icon(self, *args):
        if not self.decor_enabled:
            return

        label = Label(
            text=self.current_icon,
            font_name='fnt/segmdl2.ttf',
            color=theme.bg)
        label.texture_update()

        tex = label.texture

        for decor in self.decors:
            decor.texture = tex

        self.all_decor_rotation()

    def clear_decor(self):
        self.canvas.remove_group('decor')


class OverdrawLabel(FloatLayout):
    icon = StringProperty()
    text = StringProperty()
    widget = ObjectProperty()
    angle = NumericProperty(0)
    __MAX_TILT = 4

    @mainthread
    def __init__(self, **kw):
        super().__init__(**kw)

        for child in self.widget.children:
            if isinstance(child, OverdrawLabel):
                child.dismiss()

        self.widget.overdrawer = self
        self.widget.add_widget(self)

        Animation.stop_all(self)
        Animation(opacity=1, d=.2).start(self)
        if Config.get('animations', True):
            anim = (
                Animation(angle=self.__MAX_TILT, d=.3, t='in_out_expo') +
                Animation(angle=0, d=1, t='out_elastic') + Animation(d=2) +
                Animation(angle=self.__MAX_TILT * -1, d=.3, t='in_out_expo') +
                Animation(angle=0, d=1, t='out_elastic') + Animation(d=2))
            anim.repeat = True
            anim.start(self)

    def dismiss(self, *args):
        Animation.stop_all(self)
        anim = Animation(opacity=0, d=.2)
        anim.bind(on_complete=lambda *args: self.widget.remove_widget(self))
        anim.start(self)


class SmoothScrollView(SmoothScrollView):
    # Has to be here for the rule to be applied
    pass


class GameCollection(SmoothScrollView):
    COMMON_PATHS_URL = 'https://raw.githubusercontent.com/XtremeWare/XtremeUpdater/master/res/CommonPaths.yaml'
    COMMON_PATHS_CACHE_PATH = '.cache/common/paths/CommonPaths.yaml'
    CUSTOM_PATHS_PATH = '.config/CustomPaths.json'
    datastore = DictProperty()
    custom_paths = DictProperty()

    def update_custom_games(self):
        if os.path.isfile(self.CUSTOM_PATHS_PATH):
            self.custom_paths = JsonStore(self.CUSTOM_PATHS_PATH)

    def update_local_games(self):
        self.update_custom_games()

        if os.path.isfile(self.COMMON_PATHS_CACHE_PATH):
            with open(self.COMMON_PATHS_CACHE_PATH) as stream:
                self.datastore = yaml.safe_load(stream)

        def on_request_success(req, result):
            self.datastore = yaml.safe_load(result)

            os.makedirs(
                os.path.dirname(self.COMMON_PATHS_CACHE_PATH), exist_ok=True)

            with open(self.COMMON_PATHS_CACHE_PATH, 'w') as stream:
                yaml.dump(dict(self.datastore), stream)

        def on_request_error(*args):
            app.root.bar.error_ping()

        UrlRequest(
            self.COMMON_PATHS_URL,
            on_request_success,
            on_error=on_request_error)

    def on_custom_paths(self, *args):
        custom_paths = dict(self.custom_paths)
        for child in self.ids.board.children:
            if child.text in custom_paths:
                del custom_paths[child.text]

        for game, data in custom_paths.items():
            path = data['path']
            launch_path = data['launchPath']

            button = GameButton(
                text=game, path=path, exe=launch_path, custom=True)
            self.ids.board.add_widget(button)
            button.update_image()

    def on_datastore(self, *args):
        drives = win32api.GetLogicalDriveStrings()
        drives = drives.split('\000')[:-1]

        datastore = dict(self.datastore)
        for child in self.ids.board.children:
            if child.text in datastore:
                del datastore[child.text]

        for drive in drives:
            for game, data in datastore.items():
                path = data.get('path', '')
                launch_path = data.get('launchPath', '')
                expand_patch = data.get('expandUserPatch', False)
                expand_launch = data.get('expandUserLaunch', False)
                is_url = data.get('isURL', False)

                if not expand_patch:
                    path = os.path.join(drive, path)

                if not expand_launch and not is_url:
                    launch_path = os.path.join(drive, launch_path)

                if not os.path.isdir(path):
                    continue

                button = GameButton(
                    text=game,
                    path=path,
                    exe=launch_path,
                    expand_user_patch=expand_patch,
                    expand_user_launch=expand_launch,
                    custom=False)
                self.ids.board.add_widget(button)
                button.update_image()

    def remove_from_collection(self, button):
        self.remove_popup = GameRemovePopup(
            game=button.text,
            proceed_command=lambda: self.proceed_remove_from_collection(button)
        )
        self.remove_popup.open()

    def proceed_remove_from_collection(self, button):
        self.remove_popup.dismiss()

        if os.path.isfile(self.CUSTOM_PATHS_PATH):
            store = JsonStore(self.CUSTOM_PATHS_PATH)
            store.delete(button.text)
            self.ids.board.remove_widget(button)
            app.root.bar.ping()


class CustPopup(Popup):
    icon = StringProperty()
    show_close_button = BooleanProperty(False)
    _close_button_color = ListProperty((1, 1, 1, 1))
    _hovering_close_btn = BooleanProperty(False)
    _icon_tex = ObjectProperty()

    def __init__(self, **kw):
        super().__init__(**kw)

        if app.root:
            Clock.schedule_once(self.render_background)

        self.children[0].children[2].markup = True

        label = CoreLabel(
            text=self.icon,
            font_name='fnt/segmdl2.ttf',
            font_size=72,
            color=theme.sec,
            padding=[18, 18])
        label.refresh()
        self._icon_tex = label.texture
        self._icon_rect = self.canvas.get_group('icon')[0]

        # close button texture
        label = CoreLabel(text='\u00d7', font_size=36, size=(36, 36))
        label.refresh()
        self.canvas.after.get_group('close_button')[0].texture = label.texture
        self._close_button_color = theme.sec

        # close button hovering behavior
        Window.bind(mouse_pos=self.on_mouse_pos)

        Clock.schedule_interval(self.dance_icon, 2)

    def render_background(self, *args):
        fbo = Fbo(size=app.root.size, with_stencilbuffer=True)

        with fbo:
            Scale(1, -1, 1)
            Translate(-app.root.x, -app.root.y - app.root.height, 0)

        fbo.add(app.root.canvas)
        fbo.draw()
        fbo.remove(app.root.canvas)

        tex = fbo.texture

        img = Image.frombytes('RGBA', tex.size, tex.pixels)
        img = img.filter(ImageFilter.GaussianBlur(50))

        tex = Texture.create(size=img.size)
        tex.blit_buffer(pbuffer=img.tobytes(), size=img.size, colorfmt='rgba')
        tex.flip_vertical()
        self.canvas.before.get_group('blur')[0].texture = tex

        Window.canvas.insert(0, app.root.canvas)

    # close button hovering behavior
    def on_mouse_pos(self, __, pos):
        self._hovering_close_btn = self.collides_close_button(*pos)

    def on__hovering_close_btn(self, __, hovering):
        if hovering:
            Animation(_close_button_color=theme.prim, d=.1).start(self)
        else:
            Animation(_close_button_color=theme.sec, d=.1).start(self)

    def collides_close_button(self, x, y):
        btn = self.canvas.after.get_group('close_button')[0]
        return btn.pos[0] <= x <= btn.pos[0] + btn.size[0] and btn.pos[
            1] <= y <= btn.pos[1] + btn.size[1]

    def dance_icon(self, *args):
        curr_x, curr_y = self._icon_rect.pos
        (Animation(pos=[curr_x, curr_y + 10], d=.4, t='out_expo') + Animation(
            pos=[curr_x, curr_y], d=.2, t='out_bounce')).start(self._icon_rect)

    def on_open(self, *args):
        Animation(
            size_hint=self.final_size_hint, opacity=1, d=.5,
            t='out_expo').start(self)

    def dismiss(self, *args):
        anim = Animation(size_hint=[1, 1], opacity=0, d=.3, t='in_expo')
        anim.bind(on_complete=lambda *__: super(CustPopup, self).dismiss())
        anim.start(self)


class GameRemovePopup(CustPopup):
    game = StringProperty()
    proceed_command = ObjectProperty()


class ErrorPopup(CustPopup):
    message = StringProperty()


class RestorePopup(ErrorPopup):
    restored = ListProperty()
    not_restored = ListProperty()


class ImageCacher:
    CACHE_DIR = '.cache/img/'

    @classmethod
    def create_cache_dir(cls):
        os.makedirs(cls.CACHE_DIR, exist_ok=True)

    @classmethod
    def download_image(cls, query, AsyncImageInstance):
        if os.path.isfile(os.path.join(cls.CACHE_DIR, query)):
            return

        UrlRequest(
            TEMPLATE.format(query),
            lambda req, result: cls.on_request_success(req, result, query, AsyncImageInstance),
            req_headers=HEADERS)

    @classmethod
    def on_request_success(cls, req, result, query, AsyncImageInstance):
        cls.create_cache_dir()

        def load_image(index):
            def on_request_success(req, result):
                buffer = BytesIO(result)
                img = Image.open(buffer)
                img = cropped_thumbnail(img, [333, 187])
                img.save(cls.CACHE_DIR + query, 'PNG')

                AsyncImageInstance.reload()

            UrlRequest(
                get_image_url_from_response(result, index),
                on_success=on_request_success,
                on_failure=lambda *args: load_image(index + 1),
                on_redirect=lambda *args: load_image(index + 1),
                req_headers=HEADERS,
                decode=False)
            AsyncImageInstance.last_image_index = index

        load_image(0)


class GameButton(Button, HoveringBehavior):
    path = StringProperty()
    exe = StringProperty()
    expand_user_launch = BooleanProperty(0)
    expand_user_patch = BooleanProperty(0)
    custom = BooleanProperty(0)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.on_leave()
        self.ids.image.bind(texture=self.update_icon_color)

    def launch_game(self):
        app.root.bar.ping()

        path = self.exe

        if self.expand_user_launch:
            path = os.path.expanduser(path)

        try:
            os.startfile(path)

        except FileNotFoundError:
            app.root.bar.error_ping()

    def remove_from_collection(self):
        self.parent.parent.remove_from_collection(self)

    def update_image(self):
        query = self.text
        query += ' logo wallpaper'
        query = query.split()
        query = '+'.join(query)

        ImageCacher.download_image(query, self.ids.image)
        self.ids.image.source = os.path.join(ImageCacher.CACHE_DIR, query)

    def update_icon_color(self, *args):
        total_w = 0
        max_h = 0

        for ch in self.icon_buttons:
            total_w += ch.width
            max_h = ch.height if ch.height > max_h else max_h

        x = self.width - total_w
        y = self.height - max_h

        # dirty fix
        if self.ids.image.texture is None:
            return

        tex = self.ids.image.texture.get_region(x, y, total_w, max_h)

        img = Image.frombytes('RGBA', (tex.size), tex.pixels)
        img.thumbnail((1, 1))
        avg_color = img.getpixel((0, 0))

        avg_color = [i / 255 for i in avg_color]

        color = font_color(avg_color)

        for ch in self.icon_buttons:
            ch.color = color

    @property
    def icon_buttons(self):
        return [
            ch for ch in self.children if isinstance(ch, Factory.IconButton)
        ]

    def on_release(self):
        path = self.path

        if self.expand_user_patch:
            path = os.path.expanduser(path)

        app.root.request_load_dlls(path)
        app.root.launch_path = self.exe


class NavigationButton(CustButton):
    __active = False
    page_index = NumericProperty()
    icon = StringProperty()
    highlight_height = NumericProperty()
    highlight_width = NumericProperty()
    highlight_width_ratio = .8
    highlight_color = ListProperty([0, 0, 0, 0])

    def __init__(self, **kw):
        super().__init__(**kw)

        self.highlight_color = theme.prim

    def highlight(self):
        self.__active = True
        Animation.stop_all(self)
        (Animation(
            highlight_width=self.width,
            highlight_color=theme.sec,
            color=self._orig_attrs.get('color', self.color),
            d=.5,
            t='out_expo') & Animation(
                highlight_height=self.height, d=.3,
                t='in_out_quint')).start(self)

    def nohighghlight(self):
        self.__active = False
        Animation.stop_all(self)
        (Animation(
            highlight_width=self.width * self.highlight_width_ratio,
            highlight_color=theme.prim,
            d=.1,
            t='in_expo') & Animation(
                highlight_height=0, d=.1, t='in_out_quint')).start(self)

    def on_leave(self, *args, **kw):
        if not self.__active and not self.disabled:
            super().on_leave(*args, **kw)
            Animation(highlight_height=0, d=.2, t='out_expo').start(self)

    def on_enter(self, *args, **kw):
        if not self.__active and not self.disabled:
            super().on_enter(*args, **kw)
            Animation(highlight_height=3, d=.2, t='out_expo').start(self)

    def on_release(self):
        if not self.__active:
            super().on_release()
            self.parent.active = self.page_index
            app.root.ids.header_label.current_icon = self.icon


class Navigation(BoxLayout, NoiseTexture):
    active = NumericProperty()
    __last_highlight = 0
    page_layout = ObjectProperty()
    tabs = ListProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        Clock.schedule_once(self._init_highlight)

    def _init_highlight(self, *args):
        Clock.schedule_once(lambda *args: self.tabs[self.active].highlight())

    def on_children(self, Navigation, children):
        self.tabs = [
            child for child in children if isinstance(child, NavigationButton)
        ][::-1]

    def on_active(self, *args):
        self.tabs[self.__last_highlight].nohighghlight()
        self.tabs[self.active].highlight()

        self.page_layout.page = self.active
        self.__last_highlight = self.active


class Content(PageLayout):
    commands = DictProperty()

    def on_page(self, _, page):
        try:
            self.parent.ids.navigation.active = page
        except IndexError:
            pass

        try:
            self.commands[page]()
        except KeyError:
            pass


class DllViewItem(RecycleDataViewBehavior, CustButton):
    index = None
    selected = BooleanProperty()
    over_color_alpha = NumericProperty()
    rv = None

    def __init__(self, **kw):
        super().__init__(*kw)

        self._update_colors()

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''

        self.rv = rv
        self.index = index
        return super().refresh_view_attrs(rv, index, data)

    def on_press(self):
        self.selected = not self.selected
        self.rv.select_by_index_from_view(self.index, self.selected)

    def on_selected(self, *args):
        Animation.stop_all(self)
        self._update_colors()

    def _update_colors(self, *args):
        if self.selected:
            Animation(
                background_color=theme.prim, color=theme.sec, d=.1).start(self)

        else:
            Animation(
                background_color=theme.sec, color=theme.fg, d=.1).start(self)


class DllView(RecycleView):
    dlls = ListProperty()
    selected_nodes = ListProperty()

    def on_dlls(self, __, dlls):
        self.data = [{
            'text': dll,
            'selected': dll in self.selected_nodes
        } for dll in dlls]

    def _update_selected_nodes(self, *args):
        self.selected_nodes = [
            item for item in self.data if item.get('selected', False)
        ]

    def invert_selection(self):
        ''' Selects all nodes if some or none are already selected and deselects all nodes if all nodes are currently selected. '''

        self.deselect_all() if len(self.selected_nodes) == len(
            self.data) else self.select_all()

    def select_by_text(self, items: list):
        ''' Selects nodes which text is in the items list argument. '''

        for item in self.data:
            item['selected'] = item.get('text', '') in items

        self._update_selected_nodes()

        self.refresh_from_data()

    def select_by_index_from_view(self, index, selected):
        ''' Selects / deselects a node on given index. '''

        self.data[index]['selected'] = selected
        self._update_selected_nodes()

    def select_by_index(self, *args):
        self.select_by_index_from_view(*args)
        self.refresh_from_data()

    def select_all(self):
        ''' Selects all nodes. '''

        for item in self.data:
            item['selected'] = True

        self._update_selected_nodes()

        self.refresh_from_data()

    def deselect_all(self):
        ''' Deselects all nodes. '''

        for item in self.data:
            item['selected'] = False

        self._update_selected_nodes()

        self.refresh_from_data()

    def on_scroll_start(self, *args):
        super().on_scroll_start(*args)
        self.refresh_views_hovering()

    def on_scroll_move(self, *args):
        super().on_scroll_start(*args)
        self.refresh_views_hovering()

    def refresh_views_hovering(self):
        for child in self.layout_manager.children:
            child.refresh_hovering()


class SyncPopup(Popup, NoiseTexture):
    icon_rotation = NumericProperty()

    def __init__(self, **kw):
        super().__init__(**kw)

        if Config.get('animations', True):
            Clock.schedule_interval(self.rotate_icon, 2)

    def rotate_icon(self, *args):
        Animation(
            icon_rotation=self.icon_rotation - 180, d=2,
            t='out_elastic').start(self)

    def dismiss(self):
        Animation(opacity=0, d=.5).start(self)
        Clock.schedule_once(lambda *args: super(Popup, self).dismiss(), 1)


class LaunchNowButton(CustButton):
    def __init__(self, **kw):
        super().__init__(**kw)

        anim = (Animation(padding_y=self.padding_y + 5, d=.2, t='out_expo') +
                Animation(padding_y=self.padding_y, d=.2,
                          t='out_bounce') + Animation(d=2))
        anim.repeat = True
        anim.start(self)

    def on_release(self):
        app.root.launch_updated()

        (Animation(opacity=0, d=.5, t='out_expo') + Animation(
            height=0, d=.5, t='out_expo')).start(self)
        Clock.schedule_once(
            lambda *args: app.root.ids.content_updater.remove_widget(self), 1)


class WorkingBar(Widget):
    color = ListProperty()
    _x1 = NumericProperty()
    _x2 = NumericProperty()

    def ping(self):
        if hasattr(self, 'working_anim'):
            return

        self._x1, self._x2 = 0, 0
        (Animation(_x1=0, _x2=1, d=.5, t='out_expo') + Animation(
            _x1=1, d=.5, t='out_expo')).start(self)

    def error_ping(self):
        self.color = [1, .3, .3, 1]
        self.ping()
        Clock.schedule_once(lambda *args: setattr(self, 'color', theme.prim),
                            1)

    def work(self):
        self.working_anim = Animation(
            _x1=0, _x2=0, d=.5, t='out_expo') + Animation(
                _x1=0, _x2=1, d=.5, t='out_expo') + Animation(
                    _x1=1, _x2=1, d=.5, t='out_expo') + Animation(
                        _x1=0, _x2=1, d=.5, t='out_expo')
        self.working_anim.repeat = True
        self.working_anim.start(self)

    def unwork(self):
        if hasattr(self, 'working_anim'):
            self.working_anim.bind(on_complete=self.clear)
            self.working_anim.repeat = False
            del self.working_anim

    def clear(self, *args):
        Clock.schedule_once(
            lambda *args: Animation(_x1=0, _x2=0, d=.5, t='out_expo').start(self)
        )

    def set_value(self, value: float):
        self.unwork()
        Animation.stop_all(self)
        Animation(_x1=0, _x2=value, d=.5, t='out_expo').start(self)


class IsAdminNotif(Notification):
    title_template = '{} as admin'
    message_template = '{} tweaks are available.'

    def __init__(self, **kw):
        super().__init__(**kw)

        self.title_ = self.title_template.format(
            '[color=5f5]Running[/color]'
            if IS_ADMIN else '[color=f55]Not running[/color]')
        self.message = self.message_template.format(
            '[color=5f5]All[/color]'
            if IS_ADMIN else '[color=f55]Only some[/color]')


class RunAsAdminButton(ModalView, HoveringBehavior):
    _border_points = ListProperty([0, 0, 0, 0, 0, 0])
    _disp_icon = NumericProperty(1)
    _btn_opacity = NumericProperty(1)
    _border_template = [
        [0, 1, 0, 1, 0, 1],
        [0, 1, 1, 1, 1, 1],
        [0, 1, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 0],
        [1, 0, 1, 0, 1, 0],
        [1, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 1],
    ]

    def __init__(self, **kw):
        super().__init__(**kw)

        if not Config.get('animations', True):
            return

        anim = Animation(d=0)
        for points in self._border_template:
            anim += Animation(_border_points=points, d=.3, t='in_out_quint')

        anim.repeat = True
        anim.start(self)

    def ping(self):
        self.hovering = True
        Clock.schedule_once(lambda *args: setattr(self, 'hovering', False), 4)

    def on_touch_down(self, *args):
        pass

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            Logger.info('Executing as admin...')

            ok = ctypes.windll.shell32.ShellExecuteW(
                None, 'runas', sys.executable,
                '' if hasattr(sys, '_MEIPASS') else __file__, None, 1) > 32

            Logger.info('Successfully executed as admin'
                        if ok else 'Failed to execute as admin')

            if ok:
                app.stop()

    def on_touch_move(*args):
        pass

    def on_hovering(self, *args):
        try:
            self.fade_anim.cancel(self)
        except AttributeError:
            pass

        self.fade_anim = (
            Animation(width=200 if self.hovering else 60, d=.5, t='out_expo') &
            Animation(_disp_icon=not self.hovering, d=.2) &
            (Animation(_btn_opacity=0, d=.1) + Animation(_btn_opacity=1, d=.1))
        )
        self.fade_anim.start(self)


class ThemeSwitcher(BoxLayout):
    themes = ListProperty()
    theme = ObjectProperty()
    display_color = ListProperty([0, 0, 0, 0])
    display_colors = []
    display_height = NumericProperty()

    def __init__(self, **kw):
        super().__init__(**kw)

        def on_frame(*args):
            self.themes = theme.ordered_available_themes
            Clock.schedule_interval(self.swap_color, 2)

        Clock.schedule_once(on_frame)

    def swap_color(self, *args):
        self.display_colors.append(self.display_colors.pop(0))

        (Animation(display_height=0, d=.2, t='in_expo') + Animation(
            display_color=self.display_colors[0], d=0) + Animation(
                display_height=self.height, d=.2, t='out_expo')).start(self)

    def on_theme(self, __, theme_):
        Config.theme = theme_.name
        self.display_colors = list(theme_.get_values_kivy_color().values())

        def on_complete(*args):
            self.ids.label.text = self.theme.decoded_name
            Animation(opacity=1, d=.2, t='out_expo').start(self.ids.label)

        anim = Animation(opacity=0, d=.2, t='in_expo')
        anim.bind(on_complete=on_complete)
        anim.start(self.ids.label)

        if theme_.name != theme.name:
            Notification(
                title_='Restart required',
                message=
                f'Please [color={theme.PRIM}]restart[/color] XtremeUpdater to set the new theme.'
            ).open()

    def on_themes(self, __, themes):
        self.theme = themes[0]

    def previous_theme(self):
        self.themes = [self.themes.pop(-1)] + self.themes

    def next_theme(self):
        self.themes.append(self.themes.pop(0))


class RootLayout(BoxLayout, HoveringBehavior):
    dlls_loaded = BooleanProperty(False)
    listed_dlls = ListProperty()
    path = StringProperty()

    # mouse highlight
    _mouse_highlight_pos = ListProperty((0, 0))
    _highlight_alpha = NumericProperty()
    _mouse_highlight_anim = Animation()
    _can_highlight = BooleanProperty(False)

    # options
    mouse_highlight = BooleanProperty(Config.get('mouse_highlight', True))

    def __init__(self, **kw):
        super().__init__(**kw)

        self.bar = self.ids.bar

        # mouse highlight
        self.on_mouse_highlight(None, self.mouse_highlight)

        def callback(*__):
            if self.mouse_highlight:
                self._highlight_alpha = 0
                self._can_highlight = True
                self._show_highlight()
                Window.unbind(mouse_pos=callback)

        Window.bind(mouse_pos=callback)

        # sync
        def on_frame(*args):
            self.show_sync_popup()
            self.setup_updater()

        Clock.schedule_once(on_frame)

    # mouse highlight
    def _show_highlight(self, *__):
        self._mouse_highlight_anim.stop(self)
        self._mouse_highlight_anim = Animation(_highlight_alpha=1, d=.1)
        self._mouse_highlight_anim.start(self)

    def _hide_highlight(self, *__):
        self._mouse_highlight_anim.stop(self)
        self._mouse_highlight_anim = Animation(_highlight_alpha=0, d=.2)
        self._mouse_highlight_anim.start(self)

    def _update_highlight(self, __, pos):
        self._mouse_highlight_pos = pos[0] - 60, pos[1] - 60

    def on_mouse_highlight(self, __, is_on):
        if is_on:
            Window.bind(
                mouse_pos=self._update_highlight,
                on_cursor_enter=self._show_highlight,
                on_cursor_leave=self._hide_highlight)
            self._update_highlight(Window, Window.mouse_pos)
            self._show_highlight()
        else:
            Window.unbind(
                mouse_pos=self._update_highlight,
                on_cursor_enter=self._show_highlight,
                on_cursor_leave=self._hide_highlight)
            self._hide_highlight()
        Config.mouse_highlight = is_on

    def show_sync_popup(self):
        self.sync_popup = SyncPopup()
        self.sync_popup.open()

    @new_thread
    def setup_updater(self):
        self.updater = DllUpdater()
        self.dlls_loaded = self.updater.load_available_dlls()

        if self.dlls_loaded:
            self.ids.refresh_button.disabled = True
            OverdrawLabel(
                widget=self.ids.quickupdate_content,
                icon='\uf12b',
                text='Select a directory')

        else:
            self.ids.refresh_button.disabled = False
            OverdrawLabel(
                widget=self.ids.quickupdate_content,
                icon='\uea6a',
                text='Error when syncing')

        Clock.schedule_once(self.update_common_paths)

    def update_common_paths(self, *args):
        self.ids.game_collection_view.update_local_games()
        self.after_synced()

    def after_synced(self):
        self.sync_popup.dismiss()
        if not IS_ADMIN:
            self.run_as_admin_shown = self.run_as_admin_shown
            if hasattr(self, 'admin_btn'):
                self.admin_btn.ping()

    def switch_animations_enabled(self, _, value):
        Config.animations = value
        Notification(
            title_='Restart required',
            message=
            f'A [color={theme.PRIM}]restart[/color] may be required to [color={theme.PRIM}]{"enable" if value else "disable"}[/color] animations.'
        ).open()

    @property
    def run_as_admin_shown(self):
        return Config.get('run_as_admin_shown', True)

    @run_as_admin_shown.setter
    def run_as_admin_shown(self, value):
        if value:
            self.admin_btn = RunAsAdminButton()
            self.admin_btn.open()
        elif hasattr(self, 'admin_btn'):
            self.admin_btn.dismiss()
            del self.admin_btn

        Config.run_as_admin_shown = value

    @new_thread
    def load_directory(self):
        self.request_load_dlls(easygui.diropenbox())

    def request_load_dlls(self, path):
        if not path:
            return False

        path = os.path.abspath(path)

        self.launch_path = None
        self.path = path
        self.ids.path_info.text = path
        self.ids.selective_update_btn.disabled = True
        self.ids.update_all_btn.disabled = True

        if not os.path.isdir(path):
            return False

        notif = WorkingNotif(text='Searching for dlls')
        notif.open(animation=1)
        Clock.schedule_once(lambda *__: self._load_dlls(path, notif), .5)

    def _load_dlls(self, path, notif=None):
        try:
            self.ids.content_updater.remove_widget(self.launch_now_btn)
        except AttributeError:
            pass

        self.ids.quickupdate_content.overdrawer.dismiss()

        self.listed_dlls = []

        for relative_path in self.updater.local_dlls(path):
            if relative_path.split('\\')[-1] in self.updater.available_dlls:
                self.listed_dlls.append(relative_path)

        if not self.listed_dlls:
            ErrorPopup(
                title='No dlls found here!',
                message=
                f'We are sorry. We have not found any dlls to update here in\n[color={theme.PRIM}]{path}[/color].'
            ).open()

        else:
            self.ids.selective_update_btn.disabled = False
            self.ids.update_all_btn.disabled = False

            if Config.get('show_disclaimer', True):
                Clock.schedule_once(
                    lambda *args: Factory.DisclaimerPopup().open())
                Config.show_disclaimer = False

        self.goto_page(0)
        self.bar.ping()
        if notif:
            notif.dismiss()

    def load_selective(self):
        self.goto_page(5)

        self.ids.dll_view.dlls = self.listed_dlls

        last_selected = ConfLastDlls.get_list(self.path)

        if last_selected:
            self.ids.dll_view.select_by_text(last_selected)
        elif not self.ids.dll_view.selected_nodes:
            self.ids.dll_view.select_all()

    @new_thread
    def update_callback(self, from_selection=False):
        self.goto_page(0)
        self.ids.invert_selection_button.disabled = True
        OverdrawLabel(
            widget=self.ids.quickupdate_content,
            icon='\ue896',
            text='Updating dlls..')

        if from_selection:
            dlls = [
                item.get('text', '')
                for item in self.ids.dll_view.selected_nodes
            ]
            ConfLastDlls.set_list(self.path, dlls)
        else:
            dlls = self.listed_dlls

        Notification(
            title_=f'Updating {len(dlls)} dlls',
            message=
            f'This can take a [color={theme.PRIM}]while[/color] depending on your [color={theme.PRIM}]internet speed[/color].'
        ).open()

        try:
            self.updater.update_dlls(self.path, dlls)

        except Exception:
            ErrorPopup(
                title='Failed to update dlls!',
                message=
                f'Something happened and we are not sure what it was. Please contact our support from the settings.\n\n[color=f55]{format_exc()}[/color]'
            ).open()
            OverdrawLabel(
                widget=self.ids.quickupdate_content,
                icon='\uea39',
                text='Update failed')

        else:
            OverdrawLabel(
                widget=self.ids.quickupdate_content,
                icon='\ue930',
                text='Completed')

            if self.launch_path:
                self.launch_now_btn = LaunchNowButton()
                self.ids.content_updater.add_widget(
                    self.launch_now_btn, index=0)

        self.ids.dll_view.data = []

    def launch_updated(self):
        os.startfile(self.launch_path)

    def restore_callback(self):
        dlls = [
            item.get('text', '') for item in self.ids.dll_view.selected_nodes
        ]
        restored, not_restored = self.updater.restore_dlls(self.path, dlls)

        Factory.RestorePopup(
            restored=restored, not_restored=not_restored).open()

    @silent_exc
    def clear_images_cache(self):
        shutil.rmtree(os.path.join(os.getcwd(), ImageCacher.CACHE_DIR))

    @silent_exc
    def clear_common_paths_cache(self):
        os.remove(GameCollection.COMMON_PATHS_CACHE_PATH)

    def goto_page(self, index):
        self.ids.content.page = index

    def game_path_button_callback(self):
        path = easygui.diropenbox()
        if not path:
            path = ''

        self.ids.game_add_form_dir.text_ = path

    def game_launch_path_button_callback(self):
        path = easygui.fileopenbox(
            filetypes=['*.exe', '*.url'],
            default=self.ids.game_add_form_dir.text + '\\*.exe')
        if not path:
            path = ''

        self.ids.game_add_form_launch.text_ = path

    def add_game_callback(self):
        game_name = self.ids.game_name_input.text
        game_patch_dir = self.ids.game_add_form_dir.text
        game_launch_path = (self.ids.game_add_form_launch.text
                            if self.ids.game_add_form_launch.text else
                            self.ids.url_input.text)

        if not (game_name and game_patch_dir and game_launch_path):
            return

        os.makedirs('.config', exist_ok=True)

        if not game_launch_path:
            game_launch_path = self.ids.game_add_form_launch.text

        data = {
            'path': game_patch_dir,
            'launchPath': game_launch_path,
        }

        store = JsonStore(GameCollection.CUSTOM_PATHS_PATH)
        store.put(game_name, **data)

        self.cancel_add_game_callback()
        self.ids.game_collection_view.update_custom_games()

    def cancel_add_game_callback(self):
        self.ids.game_name_input.text = ''
        self.ids.game_add_form_dir.text_ = ''
        self.ids.game_add_form_launch.text_ = ''
        self.ids.url_input.text = ''
        self.goto_page(1)

    @silent_exc
    def reset_custom_paths(self):
        os.remove(GameCollection.CUSTOM_PATHS_PATH)

    def uninstall_prompt(self):
        self.uninstall_popup = Factory.UninstallPopup()
        self.uninstall_popup.open()

    @silent_exc
    def export_logs(self):
        OUTPUT = os.path.expanduser('~\\Desktop\\XtremeUpdater_Logs.zip')
        SOURCE = os.path.abspath('logs\\')

        Logger.info(f"Trying to export logs from {SOURCE} to {OUTPUT}")

        try:
            shutil.make_archive(OUTPUT, 'zip', SOURCE)
        except:
            Logger.error(
                f"Failed to export logs from {SOURCE} to {OUTPUT}\n{format_exc()}"
            )
            raise
        else:
            Logger.info(
                f"Successfully exported logs from {SOURCE} to {OUTPUT}")

        Notification(
            title_='Logs exported',
            message=
            f'[color={theme.PRIM}]Logs[/color] were exported to [color={theme.PRIM}]{OUTPUT}[/color]',
            height=160).open()


class ConfLastDlls:
    PATH = '.config/LastDlls.yaml'

    @classmethod
    def __ensure_file(cls):
        if not os.path.isfile(cls.PATH):
            cls.__create_file()
            return False
        else:
            return True

    @classmethod
    def __create_file(cls):
        os.makedirs(os.path.dirname(cls.PATH), exist_ok=True)
        open(cls.PATH, 'w').close()

    @classmethod
    def __lasts(cls):
        cls.__ensure_file()

        with open(cls.PATH, 'r') as f:
            data = yaml.safe_load(f)

        if isinstance(data, dict):
            return data
        else:
            return {}

    @classmethod
    def set_list(cls, path: str, dlls: list):
        path = os.path.abspath(path)

        store = cls.__lasts()
        store[path] = dlls

        with open(cls.PATH, 'w') as stream:
            stream.write(yaml.dump(store))

    @classmethod
    def get_list(cls, path):
        path = os.path.abspath(path)

        try:
            return cls.__lasts()[path]
        except KeyError:
            return False


class XtremeUpdaterApp(App):
    def on_start(self):
        # Check for updates
        if hasattr(sys, 'frozen'):  # or True: # debug
            REPO_PATH = os.path.abspath(
                os.path.join(os.path.dirname(sys.executable), os.pardir))
            # REPO_PATH = r"C:\Users\jakub\AppData\Local\XtremeUpdater\repo" # debug
            self.update_client = UpdateClient(REPO_PATH)
            if self.update_client.is_update_available() or Config.get(
                    'force_update', False):  # or True: # debug
                Config.force_update = False
                Logger.info('UpdateClient: Application considered as outdated')
                self.update_notif = WorkingNotif(text='Downloading an update')
                self.update_notif.open()
                self._download_update()
            else:
                Logger.info(
                    'UpdateClient: Application considered as up-to-date')

    def on_stop(self):
        Config.dump_to_file()

    @new_thread
    def _download_update(self):
        # Download update utility and display a popup
        if not self.update_client.is_newest_util():
            Logger.info(
                'UpdateClient: Hashes do not match. Need to download fresh update-utility'
            )
            if not self.update_client.download_util():
                return
        else:
            Logger.info(
                'UpdateClient: Hashes match. Fresh update-utility not needed')
        self.update_notif.dismiss()
        Clock.schedule_once(lambda *__: Factory.UpdateRestartPopup().open(), 0)

    def _restart_for_update(self):
        # Dismiss popup and run update utility
        if hasattr(self, 'update_notif'):
            self.update_notif.dismiss()

        self.update_client.run_util()
        self.stop()

    def open_settings(self):
        self.root.goto_page(3)


Logger.info('Reading theme..')
theme = Theme(name=Config.get('theme', 'default'))

if __name__ == '__main__':
    Logger.info(f'System = {platform.system()}')
    Logger.info(f'Release = {platform.release()}')

    Window.clearcolor = theme.dark

    app = XtremeUpdaterApp()

    # set attributes required by .kv file
    app.Config = Config
    app.version = __version__
    app.theme = theme
    app.as_admin = IS_ADMIN

    app.run()
