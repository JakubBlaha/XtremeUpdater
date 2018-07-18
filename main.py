from easygui import diropenbox
from _thread import start_new
from webbrowser import open as openurl
import yaml
import os
import kivy
import win32api
import shutil
kivy.require('1.10.1')

from kivy import Config
Config.set('graphics', 'multisamples', 0)  # Hotfix for OpenGL detection bug
Config.set('graphics', 'width', 1000)
Config.set('graphics', 'height', 550)
Config.set('graphics', 'borderless', 1)
Config.set('graphics', 'resizable', 0)
Config.set('input', 'mouse', 'mouse, disable_multitouch')
Config.set('kivy', 'icon', 'img/icon.png')

from kivy.app import App
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.clock import Clock, mainthread
from kivy.network.urlrequest import UrlRequest
from kivy.adapters.listadapter import ListAdapter

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.pagelayout import PageLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.uix.listview import ListItemButton
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty, ObjectProperty, DictProperty, ListProperty, NumericProperty, BooleanProperty

from dll_updater import DllUpdater
from hovering_behavior import RelativeLayoutHoveringBehavior, HoveringBehavior
from get_image_url import get_image_url_from_response, TEMPLATE, HEADERS
from theme import *

Window.clearcolor = sec

app = App.get_running_app


def info(text):
    app().root.info(text)


def new_thread(fn):
    def wrapper(*args, **kwargs):
        start_new(fn, args, kwargs)

    return wrapper


class CustButton(Button, HoveringBehavior):
    background_hovering = StringProperty('img/button_noise_with_border.png')
    color_hovering = ListProperty(prim)
    background_color_hovering = ListProperty(disabled)

    def __init__(self, **kw):
        super().__init__(**kw)

        def on_frame(*args):
            self.orig_background_color = self.background_color
            self.orig_color = self.color

        Clock.schedule_once(on_frame, 0)

    def on_enter(self):
        if not self.disabled:
            self.orig_background_normal = self.background_normal
            Animation(
                color=self.color_hovering,
                background_color=self.background_color_hovering,
                d=.1).start(self)
            self.background_normal = self.background_hovering

    def on_leave(self):
        if not self.disabled:
            Animation(
                color=self.orig_color,
                background_color=self.orig_background_color,
                d=.1).start(self)
            self.background_normal = self.orig_background_normal

    def on_disabled(self, *args):
        if self.disabled:
            Animation(opacity=0, d=.1).start(self)

        else:
            Animation(opacity=1, d=.1).start(self)


class OverdrawLabel(FloatLayout):
    icon = StringProperty()
    text = StringProperty()
    wg = ObjectProperty()
    TEMPLATE = '[size=72][font=fnt/segmdl2.ttf]{}[/font][/size]\n{}'

    @mainthread
    def __init__(self, wg, icon, text, **kw):
        self.wg = wg
        self.icon = icon
        self.text = text

        super().__init__(**kw)

        for child in wg.children:
            if isinstance(child, OverdrawLabel):
                child.dismiss()

        wg.overdrawer = self
        wg.add_widget(self)

        Animation.stop_all(self)
        Animation(opacity=1, d=.2).start(self)

    @mainthread
    def dismiss(self, *args):
        Animation.stop_all(self)
        anim = Animation(opacity=0, d=.2)
        anim.bind(on_complete=lambda *args: self.wg.remove_widget(self))
        anim.start(self)


class GameCollection(ScrollView):
    COMMON_PATHS_URL = 'https://raw.githubusercontent.com/XtremeWare/XtremeUpdater/master/res/CommonPaths.yaml'
    COMMON_PATHS_CACHE_PATH = '.cache/common/paths/CommonPaths.yaml'
    datastore = ObjectProperty()

    def update_local_games(self):
        info('Syncing with GitHub | Please wait..')

        if os.path.isfile(self.COMMON_PATHS_CACHE_PATH):
            with open(self.COMMON_PATHS_CACHE_PATH) as stream:
                self.datastore = yaml.safe_load(stream)

        def on_request_success(req, result):
            self.datastore = yaml.safe_load(result)

            os.makedirs(
                os.path.dirname(self.COMMON_PATHS_CACHE_PATH), exist_ok=True)

            with open(self.COMMON_PATHS_CACHE_PATH, 'w') as stream:
                yaml.dump(self.datastore, stream)

            info('Successfully synced with GitHub | Updated database')

        def on_request_error(*args):
            info('Failed to sync with GiHub | Cached version may be available')

        UrlRequest(self.COMMON_PATHS_URL, on_request_success, on_error=on_request_error)

    def on_datastore(self, *args):
        self.ids.board.clear_widgets()

        drives = win32api.GetLogicalDriveStrings()
        drives = drives.split('\000')[:-1]

        for drive in drives:
            for game, data in self.datastore.items():
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
                    is_url=is_url
                )
                self.ids.board.add_widget(button)
                button.update_image()

        info('Game searching finished | Select your game')


class ImageCacher:
    CACHE_DIR = '.cache/img/'

    @classmethod
    def create_cache_dir(cls):
        os.makedirs(cls.CACHE_DIR, exist_ok=True)

    @classmethod
    def download_image(cls, query, CustAsyncImageInstance):
        if os.path.isfile(os.path.join(cls.CACHE_DIR, query)):
            return

        UrlRequest(
            TEMPLATE.format(query),
            lambda req, result: cls.on_request_success(req, result, query, CustAsyncImageInstance),
            req_headers=HEADERS)

    @classmethod
    def on_request_success(cls, req, result, query, CustAsyncImageInstance):
        cls.create_cache_dir()

        def load_image(index):
            UrlRequest(
                get_image_url_from_response(result, index),
                on_success=lambda *args: CustAsyncImageInstance.reload(),
                on_failure=lambda *args: load_image(index + 1),
                on_redirect=lambda *args: load_image(index + 1),
                req_headers=HEADERS,
                file_path=os.path.join(cls.CACHE_DIR, query))
            CustAsyncImageInstance.last_image_index = index

        load_image(0)


class GameButton(Button, RelativeLayoutHoveringBehavior):
    path = StringProperty()
    exe = StringProperty()
    expand_user_launch = BooleanProperty()
    expand_user_patch = BooleanProperty()
    is_url = BooleanProperty()

    def launch_game(self):
        info(f'Launching {self.text} | Get ready')

        path = self.exe

        if self.is_url:
            openurl(path)
            return

        if self.expand_user_launch:
            path = os.path.expanduser(path)

        os.startfile(path)

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
        Animation(color=prim, opacity=1, d=.1).start(self.ids.label)

    def on_leave(self):
        Animation.stop_all(self)
        Animation(opacity=.5, d=.1).start(self)
        Animation(color=fg, opacity=.5, d=.1).start(self.ids.label)

    def on_release(self):
        path = self.path

        if self.expand_user_patch:
            path = os.path.expanduser(path)

        app().root.load_dll_view_data(path)
        app().root.ids.content.page = 0


class NavigationButton(CustButton):
    __active = False
    page_index = NumericProperty()

    def highlight(self):
        self.__active = True
        Animation.stop_all(self)
        Animation(background_color=prim, color=fg, d=.1).start(self)
        self.background_normal = 'img/FFFFFF-1.png'

    def nohighghlight(self):
        self.__active = False
        Animation.stop_all(self)
        Animation(background_color=dark, d=.1).start(self)
        self.background_normal = 'img/noise_texture.png'

    def on_leave(self, *args):
        if not self.__active:
            super().on_leave(*args)

    def on_enter(self, *args):
        if not self.__active:
            super().on_enter(*args)

    def on_release(self):
        if not self.__active:
            super().on_release()
            self.parent.active = self.page_index


class Navigation(BoxLayout):
    active = NumericProperty(0)
    __last_highlight = 0
    page_layout = ObjectProperty()
    tabs = ListProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        Clock.schedule_once(self._init_highlight, 0)

    def _init_highlight(self, *args):
        self.tabs[self.active].highlight()

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
        self.parent.ids.navigation.active = page
        ACTIONS = {
            1:
            lambda: self.children[3].children[0].update_local_games()  # Why do not ids work?
        }

        try:
            ACTIONS[page]()

        except KeyError:
            pass


class PlaceHolder(Label):
    message = StringProperty('Coming soon')
    icon = StringProperty('\ue946')


class DllViewItem(ListItemButton):
    selectable = BooleanProperty(False)

    def on_is_selected(self, *args):
        if self.is_selected and self.selectable:
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
    def refresh_available(self):
        try:
            app().root.ids.dll_view.overdrawer.dismiss()
            available_dlls = DllUpdater.available_dlls()

        except:
            app().root.ids.refresh_button.disabled = False
            info('Syncing failed | Please try again')
            OverdrawLabel(app().root.ids.dll_view, '\uea6a',
                          'Error when syncing')

        else:
            app().root.ids.refresh_button.disabled = True
            info('We have found some dll updates | Please select dlls')
            app().root.ids.dll_view.overdrawer.dismiss()

            self.data = [{
                **item, 'selectable': item['text'] in available_dlls
            } for item in self.data]

            def on_frame(*args):
                app(
                ).root.ids.invert_selection_button.disabled = not self.get_selectable_views(
                )

            Clock.schedule_once(on_frame, 0)

    def on_selection_change(self, *args):
        app().root.set_dll_buttons_state(self.selection)

    def get_selectable_views(self) -> list:
        return [
            self.get_view(index) for index, item in enumerate(self.data)
            if item.get('selectable', False)
        ]

    def invert_selection(self):
        Clock.schedule_once(
            lambda *args: self.select_list(self.get_selectable_views()), 0)


class RootLayout(BoxLayout, HoveringBehavior):
    mouse_highlight_pos = ListProperty([-120, -120])

    def __init__(self, **kw):
        super().__init__(**kw)

        OverdrawLabel(self.ids.dll_view, '\uf12b', 'First, select a directory')

    def on_mouse_pos(self, _, pos):
        x, y = pos
        x, y = x - 60, y - 60
        self.mouse_highlight_pos = x, y

    def set_dll_buttons_state(self, enabled):
        self.ids.restore_button.disabled = not enabled
        self.ids.update_button.disabled = not enabled

    @new_thread
    def load_directory(self):
        self.info('Select a directory now | Waiting..')
        self.load_dll_view_data(diropenbox())

    @new_thread
    def load_dll_view_data(self, path):
        self.ids.content_updater_path_info.text = path

        if not os.path.isdir(path):
            self.info('Seems like an invalid directory | Try again')
            return

        self.set_dll_buttons_state(False)
        self.ids.invert_selection_button.disabled = True
        self.ids.refresh_button.disabled = True

        local_dlls = DllUpdater.local_dlls(path)

        if not local_dlls:
            OverdrawLabel(self.ids.dll_view, '\ue783', 'No dlls found here')
            self.info(
                'We have not found any dlls in this directory | Try selecting another one'
            )

        else:
            OverdrawLabel(self.ids.dll_view, '\uede4', 'Looking for dlls..')

            self.ids.dll_view.adapter.data = [{
                'text': item,
                'selectable': False
            } for item in local_dlls]
            self.ids.dll_view.adapter.refresh_available()
            self.ids.dll_view.adapter.invert_selection()

    @new_thread
    def update_callback(self):
        self.set_dll_buttons_state(False)
        self.ids.invert_selection_button.disabled = True
        OverdrawLabel(self.ids.dll_view, '\ue896', 'Updating dlls..')

        dlls = [item.text for item in self.ids.dll_view.adapter.selection]

        try:
            DllUpdater.update_dlls(self.ids.content_updater_path_info.text,
                                   dlls)

        except:
            self.info("Couldn't download updated dll | Please try again")
            OverdrawLabel(self.ids.dll_view, '\uea39', 'Update failed')

        else:
            self.info("We are done | Let's speed up your system now")
            OverdrawLabel(self.ids.dll_view, '\ue930', 'Completed')

    def restore_callback(self):
        self.info("Restoring | Please wait..")

        dlls = [item.text for item in self.ids.dll_view.adapter.selection]
        DllUpdater.restore_dlls(self.ids.content_updater_path_info.text, dlls)

    def clear_images_cache(self):
        try:
            shutil.rmtree(os.path.join(os.getcwd(), ImageCacher.CACHE_DIR))

        except FileNotFoundError:
            info('No cached images | Nothing was removed')

        else:
            info('Done | Removed cached images')

    def clear_common_paths_cache(self):
        try:
            os.remove(GameCollection.COMMON_PATHS_CACHE_PATH)

        except FileNotFoundError:
            info('No cached game database | Nothing was removed')

        else:
            info('Done | Removed cached game database')

    def clear_cache(self):
        try:
            shutil.rmtree(os.path.join(os.getcwd(), '.cache'))

        except FileNotFoundError:
            info('No cached files | Nothing was removed')

        else:
            info('Done | Removed cached files')

    def refresh_dll_view(self):
        self.load_dll_view_data(self.ids.content_updater_path_info.text)

    @mainthread
    def info(self, text):
        Animation.cancel_all(self.ids.info_label)

        def on_complete(*args):
            self.ids.info_label.text = text
            Animation(color=prim, d=.1).start(self.ids.info_label)

        anim = Animation(color=sec, d=.1)
        anim.bind(on_complete=on_complete)
        anim.start(self.ids.info_label)


class XtremeUpdaterApp(App):
    icon = 'img/icon.png'


if __name__ == '__main__':
    xtremeupdater = XtremeUpdaterApp()
    xtremeupdater.run()