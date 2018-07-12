from easygui import diropenbox
import urllib.request
from bs4 import BeautifulSoup
from shutil import copy
from threading import Thread
import yaml
import os
from distutils.version import StrictVersion

from theme import *
from new_thread import new_thread

import kivy
kivy.require('1.10.0')

from kivy import Config
Config.set('graphics', 'multisamples', 0)
Config.set('graphics', 'width', 1000)
Config.set('graphics', 'height', 550)
Config.set('graphics', 'borderless', 1)
Config.set('graphics', 'resizable', 0)
Config.set('input', 'mouse', 'mouse, disable_multitouch')

from kivy.app import App
from kivy.clock import Clock
from kivy.clock import mainthread
from kivy.animation import Animation
from kivy.core.window import Window
Window.clearcolor = sec

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.pagelayout import PageLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import AsyncImage
from kivy.properties import BooleanProperty, StringProperty, NumericProperty, ObjectProperty, ListProperty, DictProperty
from kivy.adapters.listadapter import ListAdapter
from kivy.uix.listview import ListItemButton
from kivy.network.urlrequest import UrlRequest

from windowdragbehavior import WindowDragBehavior
from hovering_behavior import HoveringBehavior
from custbutton import CustButton
from get_image_url import TEMPLATE, HEADERS, get_image_url_from_response

app = lambda: App.get_running_app()
info = lambda text: app().root.info(text)


def local_dlls(path):
    return [
        item for item in os.listdir(path)
        if os.path.splitext(item)[1] == '.dll'
    ]


def get_data(url):
    return urllib.request.urlopen(url).read()


class DllUpdater:
    URL = "https://github.com/XtremeWare/XtremeUpdater/tree/master/dll/"
    RAW_URL = "https://github.com/XtremeWare/XtremeUpdater/raw/master/dll/"
    BACKUP_DIR = ".backup/"

    @classmethod
    def available_dlls(cls):
        try:
            html = get_data(cls.URL)

        except:
            app().refresh_button_active = True

            info('Syncing failed | Please try again')
            OverdrawLabel(app().root.ids.dll_view, '\uea6a',
                          'Error when syncing')

            return False

        else:
            app().refresh_button_active = False

            available_dlls = []
            soup = BeautifulSoup(html, 'html.parser')
            for a in soup.find_all('a', {'class': 'js-navigation-open'}):
                if a.parent.parent.get('class')[0] == 'content':
                    available_dlls.append(a.text)

            info('We have found some dll updates | Please select dlls')
            app().root.ids.dll_view.overdrawer.dismiss()

            return available_dlls

    @classmethod
    def _download_dll(cls, dllname):
        _adress = os.path.join(cls.RAW_URL, dllname)
        _data = get_data(_adress)

        return _data

    @classmethod
    def _backup_dll(cls, path, dll):
        dst = os.path.realpath(
            os.path.join(cls.BACKUP_DIR,
                         os.path.splitdrive(path)[1][1:]))

        if not os.path.exists(dst):
            os.makedirs(dst)

        copy(os.path.join(path, dll), dst)

    @staticmethod
    def _overwrite_dll(path, data):
        with open(path, 'wb') as f:
            f.write(data)

    @classmethod
    def update_dlls(cls, path, dlls):
        dll_num = len(dlls)

        try:
            for index, dll in enumerate(dlls):
                info(
                    f"Downloading {dll} ({index + 1} of {dll_num}) | Please wait.."
                )
                data = cls._download_dll(dll)

                local_dll_path = os.path.join(path, dll)
                with open(local_dll_path, 'rb') as f:
                    local_dll_data = f.read()

                if data == local_dll_data:
                    continue

                cls._backup_dll(path, dll)
                cls._overwrite_dll(local_dll_path, data)

        except:
            info("Couldn't download updated dll | Please try again")
            OverdrawLabel(app().root.ids.dll_view, '\uea39',
                          'Dll download failed')

        else:
            info("We are done | Let's speed up your system now")
            OverdrawLabel(app().root.ids.dll_view, '\ue930', 'Completed')

    @classmethod
    def restore_dlls(cls, path, dlls):
        info("Restoring | Please wait..")

        dll_num = len(dlls)
        bck_path = os.path.abspath(
            os.path.join(cls.BACKUP_DIR,
                         os.path.splitdrive(path)[1][1:]))

        restored = 0
        for index, dll in enumerate(dlls):
            i = index + 1

            backed_dll_path = os.path.join(bck_path, dll)
            try:
                copy(backed_dll_path, path)
            except:
                pass
            else:
                restored += 1

        info(f"Restoring done | Restored {restored} of {dll_num} dlls")

    @classmethod
    def available_restore(cls, path):
        bck_path = os.path.abspath(os.path.join(cls.BACKUP_DIR, path))

        return os.listdir(bck_path)


class GameCollection(ScrollView):
    COMMON_PATHS_URL = 'https://raw.githubusercontent.com/XtremeWare/XtremeUpdater/master/res/CommonPaths.yaml'
    data = DictProperty()
    game_buttons = ListProperty()
    datastore = ObjectProperty()

    def on_data(self, _, data):
        self.ids.board.clear_widgets()

        for game, path in self.data.items():
            button = GameButton(text=game, path=path)
            self.game_buttons.append(button)
            self.ids.board.add_widget(button)

    def update_local_games(self):
        info('Syncing with GitHub | Please wait..')

        def on_request_success(req, result):
            info('Successfully synced with GitHub | Searching for games..')
            self.datastore = yaml.safe_load(result)

        UrlRequest(self.COMMON_PATHS_URL, on_request_success)

    def on_datastore(self, _, datastore):
        for game in datastore:
            for path in datastore[game]:
                if os.path.isdir(path):
                    self.data[game] = path

        # DUMMY
        # self.data = {
        #     name: 'DUMMY_PATH'
        #     for name in [
        #         'League of Legends', 'Dota 2', 'Getting Over It',
        #         'Nier: Automata', 'Hearthstone', 'Overwatch',
        #         'Heroes of the Storm'
        #     ]
        # }

        info('Game searching finished | Select your game')

        self.update_images()

    def update_images(self):
        for button in self.game_buttons:
            button.update_image()


class CustAsyncImage(AsyncImage):
    def _on_source_load(self, value):
        super()._on_source_load(value)

        self.parent.loading_image = False
        self.color = (1, 1, 1) if value else prim
        self.allow_stretch = value
        self.parent.image_ready = True

    def on_error(self, *args):
        super().on_error(*args)

        self.parent.loading_image = False

        try:
            self.parent.load_next_image()
        except IndexError:
            pass


class GameButton(Button, HoveringBehavior):
    image_ready = False
    last_image_index = 0
    loading_image = False
    path = StringProperty()

    def update_image(self, index=0):
        if self.image_ready or self.loading_image:
            return

        self.loading_image = True

        query = self.text
        query += 'logo wallpaper'
        query = query.split()
        query = '+'.join(query)

        UrlRequest(
            TEMPLATE.format(query),
            lambda req, result: self.on_request_success(req, result, index),
            req_headers=HEADERS)

    def load_next_image(self):
        self.update_image(index=self.last_image_index + 1)

    def on_request_success(self, req, result, index):
        image_url = get_image_url_from_response(result, index)
        self.last_image_index = index
        self.ids.image.source = image_url
        self.ids.image.opacity = 1

    def on_mouse_pos(self, _, pos):
        x1, y1 = self.to_window(*self.pos)
        x2, y2 = x1 + self.width, y1 + self.height
        mouse_x, mouse_y = pos

        self.hovering = x1 < mouse_x and x2 > mouse_x and y1 < mouse_y and y2 > mouse_y

    def on_hovering(self, _, is_hovering):
        if is_hovering:
            Animation(opacity=1, d=.1).start(self)
            Animation(color=prim, opacity=1, d=.1).start(self.ids.label)
        else:
            Animation(opacity=.5, d=.1).start(self)
            Animation(color=fg, opacity=.5, d=.1).start(self.ids.label)

    def on_release(self):
        app().root.load_dll_view_data(self.path)
        app().root.ids.content.page = 0


class PageSwitchBehavior():
    page_index = NumericProperty(None)

    def on_release(self):
        if not isinstance(self.page_index, int):
            raise AttributeError("Bad value for attribute 'page_index'")

        self.parent.active = self.page_index


class NavigationButton(PageSwitchBehavior, CustButton):
    anim_nohighlight = Animation(background_color=dark, d=.1)
    anim_highlight = Animation(background_color=prim, color=fg, d=.1)
    __active = False

    def highlight(self):
        self.__active = True
        self.anim_highlight.start(self)
        self.orig_background_normal = self.background_normal
        self.background_normal = 'img/FFFFFF-1.png'

    def nohighghlight(self):
        self.__active = False
        self.anim_nohighlight.start(self)
        self.background_normal = self.orig_background_normal

    def on_leave(self, *args):
        if not self.__active:
            super().on_leave(*args)

    def on_enter(self, *args):
        if not self.__active:
            super().on_enter(*args)


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
        if not isinstance(self.page_layout, PageLayout):
            raise AttributeError("Bad value for attribute 'page_layout'")

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


class OverdrawLabel(FloatLayout):
    icon = StringProperty()
    text = StringProperty()
    template = '[size=72][font=fnt/segmdl2.ttf]{}[/font][/size]\n{}'
    wg = ObjectProperty()

    @mainthread
    def __init__(self, wg, icon='\ue943', text='', **kw):
        self.wg = wg

        super().__init__(**kw)

        self.icon = icon
        self.text = text

        if hasattr(wg, 'overdrawer') and isinstance(wg.overdrawer,
                                                    OverdrawLabel):
            wg.overdrawer.dismiss()

        wg.overdrawer = self
        wg.add_widget(self)

        def on_frame(*args):
            Animation.stop_all(self)
            Animation(opacity=1, d=.2).start(self)

        Clock.schedule_once(on_frame, 0)

    @mainthread
    def dismiss(self, *args):
        def on_frame(*args):
            Animation.stop_all(self)
            anim = Animation(opacity=0, d=.2)
            anim.bind(on_complete=lambda *args: self.wg.remove_widget(self))
            anim.start(self)

        Clock.schedule_once(on_frame, 0)


class DllViewItem(ListItemButton):
    selectable = BooleanProperty(False)

    def on_is_selected(self, DllViewItem, is_selected):
        if is_selected and self.selectable:
            self.select()
        else:
            self.deselect()


class DllViewAdapter(ListAdapter):
    data_from_code = False

    def on_data(self, *args):
        if self.data_from_code or not self.data:
            return

        self.data_from_code = True

        available_dlls = DllUpdater.available_dlls()
        self.data = [{
            **item, 'selectable': item['text'] in available_dlls
        } for item in self.data]

        def on_frame(*args):
            app(
            ).root.ids.invert_selection_button.disabled = not self.get_selectable_views(
            )

        Clock.schedule_once(on_frame, 0)

        self.data_from_code = False

    def on_selection_change(self, *args):
        app().root.set_dll_buttons_state(self.selection)

    def get_selectable_views(self) -> list:
        return [
            self.get_view(index) for index, item in enumerate(self.data)
            if item['selectable']
        ]

    def invert_selection(self):
        def callback(*args):
            self.select_list(self.get_selectable_views())

        Clock.schedule_once(callback, 0)


class RootLayout(BoxLayout):
    mouse_highlight_pos = ListProperty([-120, -120])

    def __init__(self, **kw):
        super().__init__(**kw)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, _, pos):
        x, y = pos
        x, y = x - 60, y - 60
        self.mouse_highlight_pos = x, y

    def set_dll_buttons_state(self, enabled):
        self.ids.restore_button.disabled = not enabled
        self.ids.update_button.disabled = not enabled

    @new_thread
    def load_directory(self):
        info('Select a directory now | Waiting..')
        path = diropenbox()
        self.load_dll_view_data(path)

    @new_thread
    def load_dll_view_data(self, path):
        self.ids.content_updater_path_info.text = path

        if not os.path.isdir(path):
            info('Seems like an invalid directory | Try again')
            return

        self.set_dll_buttons_state(False)
        self.ids.invert_selection_button.disabled = True
        app().refresh_button_active = False

        if not local_dlls(path):
            self.ids.dll_view.overdrawer.update(
                icon='\ue783', text='No dlls found here')
            info(
                'We have not found any dlls in this directory | Try selecting another one'
            )

            return

        OverdrawLabel(self.ids.dll_view, '\uede4', 'Looking for dlls..')

        self.ids.dll_view.adapter.data = [{
            'text': item
        } for item in local_dlls(path)]

        self.ids.dll_view.adapter.invert_selection()

    def update_callback(self):
        self.set_dll_buttons_state(False)
        OverdrawLabel(self.ids.dll_view, '\ue896', 'Updating dlls..')

        dlls = [item.text for item in self.ids.dll_view.adapter.selection]
        self.ids.dll_view.adapter.data = []

        Thread(
            target=DllUpdater.update_dlls,
            args=(self.ids.content_updater_path_info.text, dlls)).start()

    def restore_callback(self):
        dlls = [item.text for item in self.ids.dll_view.adapter.selection]

        DllUpdater.restore_dlls(self.ids.content_updater_path_info.text, dlls)

    @mainthread
    def info(self, text):
        if text == self.ids.info_label.text:
            return

        Animation.cancel_all(self.ids.info_label)

        def on_complete(*args):
            self.ids.info_label.text = text
            Animation(color=prim, d=.1).start(self.ids.info_label)

        anim = Animation(color=sec, d=.1)
        anim.bind(on_complete=on_complete)
        anim.start(self.ids.info_label)


class XtremeUpdaterApp(App):
    refresh_button_active = BooleanProperty(False)

    def __init__(self, **kw):
        super().__init__(**kw)

    def build(self):
        return RootLayout()

    def on_start(self):
        OverdrawLabel(self.root.ids.dll_view, '\uf12b',
                      'First, select a directory')
        self.root.set_dll_buttons_state(False)
        Clock.schedule_once(
            lambda *args: self.root.info('Select a directory | Click the folder button'),
            2)


if __name__ == '__main__':
    xtremeupdater = XtremeUpdaterApp()
    xtremeupdater.run()