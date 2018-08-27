import easygui
import yaml
import os
import win32api
import shutil
import ctypes
from random import randint
from _thread import start_new
from traceback import format_exc
from PIL import ImageGrab, ImageFilter

import kivy
kivy.require('1.10.1')

from kivy import Config
Config.set('graphics', 'width', 1000)
Config.set('graphics', 'height', 550)
Config.set('graphics', 'borderless', 1)
Config.set('graphics', 'resizable', 0)
Config.set('input', 'mouse', 'mouse, disable_multitouch')
Config.set('kivy', 'window_icon', 'img/icon.ico')
Config.set('graphics', 'multisamples', 0)

from kivy.app import App
from kivy.factory import Factory
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.clock import Clock, mainthread
from kivy.storage.jsonstore import JsonStore
from kivy.network.urlrequest import UrlRequest
from kivy.adapters.listadapter import ListAdapter

from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.image import CoreImage
from custpagelayout import PageLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics.texture import Texture
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Rectangle, Color
from kivy.uix.label import Label, CoreLabel
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.listview import ListItemButton
from kivy.properties import StringProperty, ObjectProperty, DictProperty, ListProperty, NumericProperty, BooleanProperty

from theme import theme
from dll_updater import DllUpdater
from hovering_behavior import HoveringBehavior
from windowdragbehavior import WindowDragBehavior
from get_image_url import get_image_url_from_response, TEMPLATE, HEADERS

IS_ADMIN = ctypes.windll.shell32.IsUserAnAdmin()


def read_file(path):
    with open(path) as f:
        return f.read()


def new_thread(fn):
    def wrapper(*args, **kwargs):
        start_new(fn, args, kwargs)

    return wrapper

def silent_exc(fn):
    def wrapper(*args, **kw):
        try:
            fn(*args, **kw)
        except Exception:
            app.root.bar.error_ping()
        else:
            app.root.bar.ping()

    return wrapper


class Animation(Animation):
    def __init__(self, **kw):
        super().__init__(**kw)
        if not app.conf.animations:
            self._duration = 0


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

    def __init__(self, **kw):
        super().__init__(**kw)

        if app.conf.head_decor:
            Clock.schedule_once(
                lambda *args: Clock.schedule_once(self.setup_mini_labels))

    def setup_mini_labels(self, *args):
        for i in range(17):
            label = HeaderMiniLabel(
                text=self.current_icon, x=i * 48 + 120, y=self.y - i % 2 * 10)
            self.add_widget(label, 1)

    def on_current_icon(self, *args):
        for child in self.children:
            child.text = self.current_icon


class HeaderMiniLabel(Label, HoveringBehavior):
    rotation_angle = NumericProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        if app.conf.animations:
            Clock.schedule_once(self.rotate, randint(0, 10))
        else:
            self.unbind_hovering()

        self.rotation_angle = randint(0, 361)

    def rotate(self, *args):
        Animation(
            rotation_angle=randint(0, 1000), d=.5, t='out_expo').start(self)
        Clock.schedule_once(self.rotate, randint(5, 10))

    def on_text(self, *args):
        Animation(
            rotation_angle=self.rotation_angle + 500, d=.5,
            t='out_expo').start(self)

    def on_hovering(self, *args):
        if self.hovering:
            Animation.stop_all(self)
            (Animation(
                rotation_angle=self.rotation_angle + 500,
                color=theme.prim,
                d=.5,
                t='out_expo') + Animation(color=theme.bg, d=.5)).start(self)


class CustButton(Button, HoveringBehavior):
    color_hovering = ListProperty(theme.prim)
    background_color_hovering = ListProperty([0, 0, 0, 0])

    def on_enter(self):
        if not self.disabled:
            self.orig_background_color = self.background_color
            self.orig_color = self.color
            Animation(
                color=self.color_hovering,
                background_color=self.background_color_hovering,
                d=.1).start(self)

    def on_leave(self, force=False):
        if not self.disabled or force:
            Animation(
                color=self.orig_color,
                background_color=self.orig_background_color,
                d=.1).start(self)

    def on_disabled(self, *args):
        if self.disabled:
            Animation(opacity=.1, d=.1).start(self)
            if self.hovering:
                self.on_leave(force=True)

        else:
            Animation(opacity=1, d=.1).start(self)


class LabelIconButton(BoxLayout):
    text = StringProperty()
    icon = StringProperty()

    def __init__(self, **kw):
        super().__init__(**kw)

        def on_frame(*args):
            self.ids.label.bind(text=self.on_label_text)
            self.on_label_text()

        Clock.schedule_once(on_frame)

    def on_label_text(self, *args):
        if self.ids.label.text:
            Animation(width=40, d=.5, t='out_expo').start(self.ids.button)
            Animation(opacity=1, d=.5).start(self.ids.label)

        else:
            Animation(
                width=self.width, d=.5, t='out_expo').start(self.ids.button)
            self.ids.label.opacity = 0


class CustSwitch(Widget):
    active = BooleanProperty(False)
    _switch_x = NumericProperty(0)

    def on_active(self, *args):
        self.trigger_switch()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.active = not self.active
            self.trigger_switch()

    def trigger_switch(self):
        Animation(_switch_x=self.active * 20, d=.2, t='out_expo').start(self)


class LabelSwitch(BoxLayout):
    text = StringProperty()
    active = BooleanProperty()
    active_callback = ObjectProperty(lambda *args: None)

    def __init__(self, **kw):
        super().__init__(**kw)

        def on_frame(*args):
            self.ids.switch.bind(active=self.active_callback)

        Clock.schedule_once(on_frame)


class OverdrawLabel(FloatLayout):
    icon = StringProperty()
    text = StringProperty()
    widget = ObjectProperty()
    TEMPLATE = '[size=72][font=fnt/segmdl2.ttf]{}[/font][/size]\n{}'
    angle = NumericProperty(0)
    __MAX_TILT = 2

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
        if app.conf.animations:
            anim = (
            Animation(angle=self.__MAX_TILT, d=.3, t='in_out_expo') +
            Animation(angle=0, d=1, t='out_elastic') +
            Animation(d=1) +
            Animation(angle=self.__MAX_TILT * -1, d=.3, t='in_out_expo') +
            Animation(angle=0, d=1, t='out_elastic') +
            Animation(d=1)
            )
            anim.repeat = True
            anim.start(self)


    def dismiss(self, *args):
        Animation.stop_all(self)
        anim = Animation(opacity=0, d=.2)
        anim.bind(on_complete=lambda *args: self.widget.remove_widget(self))
        anim.start(self)
        

class GameCollection(ScrollView):
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

    def __init__(self, **kw):
        img = ImageGrab.grab()
        img = img.crop([
            Window.left, Window.top, Window.left + Window.width,
            Window.top + Window.height
        ])
        img = img.filter(ImageFilter.GaussianBlur(50))

        super().__init__(**kw)

        def on_frame(*args):
            tex = Texture.create(size=img.size)
            tex.blit_buffer(pbuffer=img.tobytes())
            tex.flip_vertical()
            self.canvas.before.get_group('blur')[0].texture = tex

        Clock.schedule_once(on_frame)

        self.children[0].children[2].markup = True

        label = CoreLabel(
            text=self.icon,
            font_name='fnt/segmdl2.ttf',
            font_size=72,
            color=theme.sec,
            padding=[18, 18])
        label.refresh()
        tex = label.texture

        with self.canvas:
            Color(1, 1, 1, 1)
            self.icon_rect = Rectangle(
                texture=tex, pos=self.pos, size=label.size)

        Clock.schedule_interval(self.dance_icon, 2)

    def on_pos(self, *args):
        self.icon_rect.pos = self.pos

    def dance_icon(self, *args):
        curr_x, curr_y = self.icon_rect.pos
        (Animation(pos=[curr_x, curr_y + 10], d=.4, t='out_expo') + Animation(
            pos=[curr_x, curr_y], d=.2, t='out_bounce')).start(self.icon_rect)

    def on_open(self, *args):
        Animation(
            size_hint=self.final_size_hint, opacity=1, d=.5,
            t='out_expo').start(self)

    def on_dismiss(self, *args):
        Animation(
            size_hint=[1, 1],
            opacity=0,
            d=.1,
            t='in_expo').start(self)


class GameRemovePopup(CustPopup):
    game = StringProperty()
    proceed_command = ObjectProperty()


class ErrorPopup(CustPopup):
    message = StringProperty()

    def on_touch_down(self, *args):
        self.dismiss()


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
                from PIL import Image
                from cropped_thumbnail import cropped_thumbnail
                from io import BytesIO

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

    def quick_update(self):
        app.root.load_dll_view_data(self.path, quickupdate=True)

    def update_image(self):
        query = self.text
        query += ' logo wallpaper'
        query = query.split()
        query = '+'.join(query)

        ImageCacher.download_image(query, self.ids.image)
        self.ids.image.source = os.path.join(ImageCacher.CACHE_DIR, query)

    def on_enter(self):
        Animation.stop_all(self)
        Animation(opacity=1, d=.1).start(self)
        Animation(opacity=1, d=.1).start(self.ids.label)

    def on_leave(self):
        Animation.stop_all(self)
        Animation(opacity=.7, d=.1).start(self)
        Animation(opacity=0, d=.1).start(self.ids.label)

    def on_release(self):
        path = self.path

        if self.expand_user_patch:
            path = os.path.expanduser(path)

        app.root.load_dll_view_data(path)
        app.root.launch_path = self.exe


class NavigationButton(CustButton):
    __active = False
    page_index = NumericProperty()
    icon = StringProperty()
    highlight_height = NumericProperty()
    highlight_width = NumericProperty()
    highlight_width_ratio = .8
    highlight_color = ListProperty(theme.prim)

    def highlight(self):
        self.__active = True
        Animation.stop_all(self)
        (
            Animation(
            highlight_width=self.width,
            highlight_color=theme.sec,
            color=theme.fg,
            d=.5,
            t='out_expo') &
            Animation(
            highlight_height=self.height,
            d=.3,
            t='in_out_quint')
        ).start(self)

    def nohighghlight(self):
        self.__active = False
        Animation.stop_all(self)
        (
            Animation(
            highlight_width=self.width * self.highlight_width_ratio,
            highlight_color=theme.prim,
            d=.1,
            t='in_expo') &
            Animation(
            highlight_height=0,
            d=.1,
            t='in_out_quint')
        ).start(self)

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
    def on_page(self, _, page):
        try:
            self.parent.ids.navigation.active = page
        except IndexError:
            pass


class PlaceHolder(Label):
    message = StringProperty('Coming soon')
    icon = StringProperty('\ue946')


class SubdirItem(Button, HoveringBehavior):
    path = StringProperty()
    highlight_width = NumericProperty()
    highlight_alpha = NumericProperty()

    def on_hovering(self, *args):
        if self.hovering:
            Animation(
                highlight_width=self.width,
                highlight_alpha=1,
                d=.3,
                t='out_expo').start(self)
        else:
            Animation(
                highlight_width=self.width * .95,
                highlight_alpha=0,
                d=.3,
                t='out_expo').start(self)


class DllViewItem(ListItemButton):
    def on_is_selected(self, *args):
        if self.is_selected:
            super().select()

            self.background_color = self.deselected_color
            Animation.stop_all(self)
            Animation(background_color=self.selected_color, d=.1).start(self)

        else:
            super().deselect()

            self.background_color = self.selected_color
            Animation.stop_all(self)
            Animation(background_color=self.deselected_color, d=.1).start(self)


class DllViewAdapter(ListAdapter):
    def on_data(self, *args):
        self.unbind(data=self.on_data)
        self.data.sort()
        self.bind(data=self.on_data)

    def on_selection_change(self, *args):
        App.get_running_app().root.set_dll_buttons_state(self.selection)

    def get_views(self) -> list:
        return [self.get_view(index) for index, __ in enumerate(self.data)]

    def invert_selection(self):
        Clock.schedule_once(lambda *args: self.select_list(self.get_views()))

    def select_by_text(self, items: list):
        views = [view for view in self.get_views() if view.text in items]
        Clock.schedule_once(lambda *args: self.select_list(views))


class SyncPopup(Popup, NoiseTexture):
    icon_rotation = NumericProperty()

    def __init__(self, **kw):
        super().__init__(**kw)

        if app.conf.animations:
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
        Clock.schedule_interval(self.animate, 2)

    def animate(self, *args):
        (Animation(padding_y=5, d=.2, t='out_expo') + Animation(
            padding_y=0, d=.2, t='out_bounce')).start(self)

    def on_release(self):
        app.root.launch_updated()

        Animation(height=0, d=1, t='out_expo').start(self)
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


class RootLayout(BoxLayout, HoveringBehavior):
    mouse_highlight_pos = ListProperty([-120, -120])
    dlls_loaded = BooleanProperty(False)

    def __init__(self, **kw):
        super().__init__(**kw)

        self.bar = self.ids.bar
        self.switch_mouse_highlight(None, app.conf.mouse_highlight)

        def on_frame(*args):
            self.show_sync_popup()
            self.setup_updater()

        Clock.schedule_once(on_frame)

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
                widget=self.ids.dll_view,
                icon='\uf12b',
                text='Select a directory')

        else:
            self.ids.refresh_button.disabled = False
            OverdrawLabel(
                widget=self.ids.dll_view,
                icon='\uea6a',
                text='Error when syncing')

        Clock.schedule_once(self.update_common_paths)

    def update_common_paths(self, *args):
        self.ids.game_collection_view.update_local_games()
        self.sync_popup.dismiss()

    def on_mouse_pos(self, _, pos):
        x, y = pos
        self.mouse_highlight_pos = x - 60, y - 60

    def switch_mouse_highlight(self, _, value):
        if value:
            self.bind_hovering()
            self.on_mouse_pos(None, Window.mouse_pos)
        else:
            self.unbind_hovering()
            self.mouse_highlight_pos = -120, -120

        app.conf.mouse_highlight = value

    def switch_animations_enabled(self, _, value):
        app.conf.animations = value
        self.ids.content.anim_kwargs['d'] = .5 * value

    def set_dll_buttons_state(self, enabled):
        self.ids.restore_button.disabled = not enabled
        self.ids.update_button.disabled = not enabled

    @new_thread
    def load_directory(self):
        self.load_dll_view_data(easygui.diropenbox())

    def load_dll_view_data(self, path, quickupdate=False):
        self.launch_path = None
        self.goto_page(0)

        if not path:
            return

        path = os.path.abspath(path)

        self.ids.path_info.text = path

        if not os.path.isdir(path):
            return

        try:
            self.ids.content_updater.remove_widget(self.launch_now_btn)
        except AttributeError:
            pass

        self.set_dll_buttons_state(False)
        self.ids.invert_selection_button.disabled = True

        local_dlls = self.updater.local_dlls(path)
        available_dlls = set(local_dlls).intersection(
            self.updater.available_dlls)

        if not available_dlls:
            ErrorPopup(
                title='No dlls found here!',
                message=
                f'We are sorry. We have not found any dlls to update here in\n[color={theme.PRIM}]{path}[/color].'
            ).open()

        else:
            self.ids.dll_view.overdrawer.dismiss()

            self.ids.dll_view.adapter.data = available_dlls
            last_selected = ConfLastDlls.get_list(path)
            if last_selected:
                self.ids.dll_view.adapter.select_by_text(last_selected)
            else:
                self.ids.dll_view.adapter.invert_selection()

            if quickupdate:
                Clock.schedule_once(lambda *args: self.update_callback())

            if app.conf.show_disclaimer:
                Factory.DisclaimerPopup().open()
                app.conf.show_disclaimer = False

        self.load_subdirs(path)

    @new_thread
    def load_subdirs(self, path):
        self.bar.work()

        self.ids.subdir_view.data = [{
            'path': subdir
        }
                                     for subdir in self.updater.dll_subdirs(
                                         path, self.updater.available_dlls)]

        self.bar.unwork()

    @new_thread
    def update_callback(self):
        self.set_dll_buttons_state(False)
        self.ids.invert_selection_button.disabled = True
        OverdrawLabel(
            widget=self.ids.dll_view, icon='\ue896', text='Updating dlls..')

        dlls = [item.text for item in self.ids.dll_view.adapter.selection]
        ConfLastDlls.set_list(self.ids.path_info.text, dlls)

        try:
            raise Exception
            self.updater.update_dlls(self.ids.path_info.text, dlls)

        except Exception:
            ErrorPopup(
                title='Failed to update dlls!',
                message=
                f'Something happened and we are not sure what it is. Please contact our support from the settings.\n\n[color=f55]{format_exc()}[/color]'
            ).open()
            OverdrawLabel(
                widget=self.ids.dll_view, icon='\uea39', text='Update failed')

        else:
            OverdrawLabel(
                widget=self.ids.dll_view, icon='\ue930', text='Completed')

            if self.launch_path:
                self.launch_now_btn = LaunchNowButton()
                self.ids.content_updater.add_widget(
                    self.launch_now_btn, index=1)

        self.ids.dll_view.adapter.data = []

    def launch_updated(self):
        os.startfile(self.launch_path)

    def restore_callback(self):
        dlls = [item.text for item in self.ids.dll_view.adapter.selection]
        self.updater.restore_dlls(self.ids.path_info.text, dlls)

        self.bar.ping()

    def clear_images_cache(self):
        try:
            shutil.rmtree(os.path.join(os.getcwd(), ImageCacher.CACHE_DIR))

        except FileNotFoundError:
            self.bar.error_ping()

        else:
            self.bar.ping()

    def clear_common_paths_cache(self):
        try:
            os.remove(GameCollection.COMMON_PATHS_CACHE_PATH)

        except FileNotFoundError:
            self.bar.error_ping()

        else:
            self.bar.ping()

    def goto_page(self, index):
        self.ids.content.page = index

    def game_path_button_callback(self):
        path = easygui.diropenbox()
        if not path:
            path = ''

        self.ids.game_add_form_dir.text = path

    def game_launch_path_button_callback(self):
        path = easygui.fileopenbox(
            filetypes=['*.exe', '*.url'],
            default=self.ids.game_add_form_dir.text + '\\*.exe')
        if not path:
            path = ''

        self.ids.game_add_form_launch.text = path

    def add_game_callback(self):
        os.makedirs('.config', exist_ok=True)

        game_name = self.ids.game_name_input.text
        game_patch_dir = self.ids.game_add_form_dir.text
        game_launch_path = self.ids.url_input.text

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
        self.ids.game_add_form_dir.text = ''
        self.ids.game_add_form_launch.text = ''
        self.ids.url_input.text = ''
        self.goto_page(1)

    def reset_custom_paths(self):
        try:
            os.remove(GameCollection.CUSTOM_PATHS_PATH)

        except FileNotFoundError:
            self.bar.error_ping()

        else:
            self.bar.ping()

    def switch_head_decor(self, _, value):
        app.conf.head_decor = value

        if value:
            self.ids.header_label.setup_mini_labels()
        else:
            self.ids.header_label.clear_widgets()

    def uninstall_prompt(self):
        self.uninstall_popup = Factory.UninstallPopup()
        self.uninstall_popup.open()

    def uninstall(self):
        LNK_PATH = os.path.expanduser(
            '~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\XtremeUpdater.lnk'
        )
        UNINST_PATH = 'C:\\XtremeUpdaterUninstall\\XtremeUpdater-Uninstall.bat'
        UNINST_DATA = ('@timeout /t 5 /nobreak\n'
                       '@rmdir /q /s %localappdata%\\XtremeUpdater\n'
                       '(goto) 2>nul & del "%~f0"')

        try:
            os.remove(LNK_PATH)
        except FileNotFoundError:
            pass

        os.makedirs(os.path.dirname(UNINST_PATH), exist_ok=True)
        with open(UNINST_PATH, 'w') as stream:
            stream.write(UNINST_DATA)

        os.startfile(UNINST_PATH)
        app.stop()

    @silent_exc
    def export_logs(self):
        OUTPUT = os.path.expanduser('~\\Desktop\\XtremeUpdater_Logs.zip')
        SOURCE = os.path.expanduser('~\\.kivy\\logs')

        shutil.make_archive(OUTPUT, 'zip', SOURCE)


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
        store = cls.__lasts()
        store[path] = dlls

        with open(cls.PATH, 'w') as stream:
            stream.write(yaml.dump(store))

    @classmethod
    def get_list(cls, path):
        try:
            return cls.__lasts()[path]
        except KeyError:
            return False


class Conf:
    __store = {}
    __path = ''

    def __init__(self, path, defaults):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        object.__setattr__(self, '__path', path)

        if os.path.isfile(path):
            with open(path, 'r') as config:
                object.__setattr__(self, '__store', {
                    **defaults,
                    **yaml.load(config)
                })
        else:
            object.__setattr__(self, '__store', defaults)

    def __setattr__(self, name, value):
        object.__getattribute__(self, '__store')[name] = value
        self.__dump_to_file()

    def __getattr__(self, name):
        return object.__getattribute__(self, '__store')[name]

    def __dump_to_file(self):
        with open(object.__getattribute__(self, '__path'), 'w') as conf:
            conf.write(yaml.dump(object.__getattribute__(self, '__store')))


class XtremeUpdaterApp(App):
    STORE_PATH = '.config/Config.yaml'
    DEFAULT_STORE = {
        'mouse_highlight': 1,
        'head_decor': 1,
        'animations': 1,
        'show_disclaimer': 1,
        'theme': 'default'
    }

    def __init__(self, **kw):
        super().__init__(**kw)
        self.load_store()

    def load_store(self):
        self.conf = Conf(self.STORE_PATH, self.DEFAULT_STORE)

    def open_settings(self):
        self.root.goto_page(4)


Window.clearcolor = theme.sec

if __name__ == '__main__':
    app = XtremeUpdaterApp()
    app.run()

__version__ = '0.5.22'
