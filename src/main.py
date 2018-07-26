from easygui import diropenbox, fileopenbox
from _thread import start_new
from webbrowser import open as openurl
import yaml
import os
import kivy
import win32api
import shutil
import ctypes
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
from kivy.storage.jsonstore import JsonStore

from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from custpagelayout import PageLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.uix.listview import ListItemButton
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, ObjectProperty, DictProperty, ListProperty, NumericProperty, BooleanProperty

from dll_updater import DllUpdater
from hovering_behavior import RelativeLayoutHoveringBehavior, HoveringBehavior
from get_image_url import get_image_url_from_response, TEMPLATE, HEADERS
from theme import *

Window.clearcolor = sec

app = App.get_running_app
is_admin = ctypes.windll.shell32.IsUserAnAdmin


def info(text):
    app().root.info(text)


def new_thread(fn):
    def wrapper(*args, **kwargs):
        start_new(fn, args, kwargs)

    return wrapper


class CustButton(Button, HoveringBehavior):
    color_hovering = ListProperty(prim)
    background_color_hovering = ListProperty(sec)

    def __init__(self, **kw):
        super().__init__(**kw)

        def on_frame(*args):
            self.orig_background_color = self.background_color
            self.orig_color = self.color

        Clock.schedule_once(on_frame)

    def on_enter(self):
        if not self.disabled:
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
            Clock.schedule_once(lambda *args: self.on_leave(force=True))

        else:
            Animation(opacity=1, d=.1).start(self)


class LabelIconButton(BoxLayout):
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
            Animation(width=self.width, d=.5, t='out_expo').start(self.ids.button)
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
    active_callback = ObjectProperty()

    def __init__(self, **kw):
        super().__init__(**kw)

        def on_frame(*args):
            self.ids.switch.bind(active=self.active_callback)
        Clock.schedule_once(on_frame)


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
    CUSTOM_PATHS_PATH = '.config/CustomPaths.json'
    datastore = DictProperty()
    custom_paths = DictProperty()

    def update_custom_games(self):
        if os.path.isfile(self.CUSTOM_PATHS_PATH):
            self.custom_paths = JsonStore(self.CUSTOM_PATHS_PATH)

    def update_local_games(self):
        info('Syncing with GitHub | Please wait..')

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

            info('Successfully synced with GitHub | Updated database')

        def on_request_error(*args):
            info('Failed to sync with GiHub | Cached version may be available')

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
            is_url = data['isURL']

            button = GameButton(
                    text=game,
                    path=path,
                    exe=launch_path,
                    is_url=is_url,
                    custom=True)
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
                    is_url=is_url,
                    custom=False)
                self.ids.board.add_widget(button)
                button.update_image()            

        info('Game searching finished | Select your game')

    def remove_from_collection(self, button):
        self.remove_popup = GameRemovePopup(game=button.text, proceed_command=lambda: self.proceed_remove_from_collection(button))
        self.remove_popup.open()

    def proceed_remove_from_collection(self, button):
        self.remove_popup.dismiss()

        if os.path.isfile(self.CUSTOM_PATHS_PATH):
            store = JsonStore(self.CUSTOM_PATHS_PATH)
            store.delete(button.text)
            self.ids.board.remove_widget(button)
            info(f'Success | Removed {button.text} from the Game Collection')

        else:
            info('Failed | Storage not found')

    def reload_mipmapping(self, enabled):
        for child in self.ids.board.children:
            child.ids.image.mipmap = enabled
            child.ids.image.reload()

        info('Mipmapping {}abled | Configuring done'.format('en' if enabled else 'dis'))


class GameRemovePopup(Popup):
    game = StringProperty()
    proceed_command = ObjectProperty()


class ImageCacher:
    CACHE_DIR = '.cache/img/'

    @classmethod
    def create_cache_dir(cls):
        os.makedirs(cls.CACHE_DIR, exist_ok=True)

    @classmethod
    def download_image(cls, query, AstncImageInstance):
        if os.path.isfile(os.path.join(cls.CACHE_DIR, query)):
            return

        UrlRequest(
            TEMPLATE.format(query),
            lambda req, result: cls.on_request_success(req, result, query, AstncImageInstance),
            req_headers=HEADERS)

    @classmethod
    def on_request_success(cls, req, result, query, AstncImageInstance):
        cls.create_cache_dir()

        def load_image(index):
            UrlRequest(
                get_image_url_from_response(result, index),
                on_success=lambda *args: AstncImageInstance.reload(),
                on_failure=lambda *args: load_image(index + 1),
                on_redirect=lambda *args: load_image(index + 1),
                req_headers=HEADERS,
                file_path=os.path.join(cls.CACHE_DIR, query))
            AstncImageInstance.last_image_index = index

        load_image(0)


class GameButton(Button, RelativeLayoutHoveringBehavior):
    path = StringProperty()
    exe = StringProperty()
    expand_user_launch = BooleanProperty(0)
    expand_user_patch = BooleanProperty(0)
    is_url = BooleanProperty()
    custom = BooleanProperty(0)

    def launch_game(self):
        info(f'Launching {self.text} | Get ready')

        path = self.exe

        if self.is_url:
            openurl(path)
            return

        if self.expand_user_launch:
            path = os.path.expanduser(path)

        os.startfile(path)

    def remove_from_collection(self):
        self.parent.parent.remove_from_collection(self)

    def quick_update(self):
        app().root.load_dll_view_data(self.path, quickupdate=True)

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
    active = NumericProperty()
    __last_highlight = 0
    page_layout = ObjectProperty()
    tabs = ListProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        Clock.schedule_once(self._init_highlight)

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
        try:
            self.parent.ids.navigation.active = page
        except IndexError:
            pass

        ACTIONS = {
            1:
            lambda: self.children[::-1][1].children[1].update_local_games()
        }

        try:
            ACTIONS[page]()

        except KeyError:
            pass


class PlaceHolder(Label):
    message = StringProperty('Coming soon')
    icon = StringProperty('\ue946')


class SubdirItem(Button, RelativeLayoutHoveringBehavior):
    path = StringProperty()
    highlight_height = NumericProperty()
    highlight_alpha = NumericProperty()

    def on_hovering(self, *args):
        if self.hovering:
            Animation(highlight_height=self.width, highlight_alpha=1, d=.5, t='out_expo').start(self)
        else:
            Animation(highlight_height=0, highlight_alpha=0, d=.5, t='out_expo').start(self)


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
        self.data = [{
            **item, 'selectable': item['text'] in DllUpdater.available_dlls
        } for item in self.data]

        def on_frame(*args):
            app(
            ).root.ids.invert_selection_button.disabled = not self.get_selectable_views(
            )

        Clock.schedule_once(on_frame)

    def on_selection_change(self, *args):
        app().root.set_dll_buttons_state(self.selection)

    def get_selectable_views(self) -> list:
        return [
            self.get_view(index) for index, item in enumerate(self.data)
            if item.get('selectable', False)
        ]

    def invert_selection(self):
        Clock.schedule_once(
            lambda *args: self.select_list(self.get_selectable_views()))


class RootLayout(BoxLayout, HoveringBehavior):
    mouse_highlight_pos = ListProperty([-120, -120])
    dlls_loaded = BooleanProperty(False)
    last_path = ''

    def __init__(self, **kw):
        super().__init__(**kw)
        self.setup_updater()
        
    @new_thread
    def setup_updater(self):
        self.info('Syncing with github | Loading dll database..')

        self.updater = DllUpdater()
        self.dlls_loaded = self.updater.load_available_dlls()

        if self.dlls_loaded:
            self.ids.refresh_button.disabled = True
            self.info('Syncing done | Successfully updated dll database')
            OverdrawLabel(self.ids.dll_view, '\uf12b', 'First, select a directory')

        else:
            self.ids.refresh_button.disabled = False
            self.info('Syncing failed | Please try again')
            OverdrawLabel(self.ids.dll_view, '\uea6a',
                          'Error when syncing')


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
    def load_dll_view_data(self, path, quickupdate=False):
        self.goto_updater()

        path = os.path.abspath(path)

        if path == self.last_path:
            self.info('Directory has not changed | Nothing to do :{')
            return

        self.last_path = path
        self.ids.content_updater_path_info.text = path

        if not os.path.isdir(path):
            self.info('Seems like an invalid directory | Try again')
            return

        self.set_dll_buttons_state(False)
        self.ids.invert_selection_button.disabled = True

        local_dlls = DllUpdater.local_dlls(path)

        if not local_dlls:
            OverdrawLabel(self.ids.dll_view, '\ue783', 'No dlls found here')
            self.info(
                'We have not found any dlls in this directory | Try selecting another one'
            )

        else:
            self.info('We have found some dll updates | Please select dlls')
            self.ids.dll_view.overdrawer.dismiss()

            self.ids.dll_view.adapter.data = [{
                'text': item,
                'selectable': False
            } for item in local_dlls]
            self.ids.dll_view.adapter.refresh_available()
            self.ids.dll_view.adapter.invert_selection()

            if quickupdate:
                Clock.schedule_once(lambda *args: self.update_callback())

        self.info('Loading subdirs | Please wait..')
        self.ids.subdir_view.data = [{'path': subdir} for subdir in DllUpdater.dll_subdirs(path, self.updater.available_dlls)]
        self.info('Subdirs loaded | Check it out!')

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

    def goto_updater(self):
        self.ids.content.page = 0

    def goto_collection(self):
        self.ids.content.page = 1

    def goto_game_add_form(self):
        self.ids.content.page = 5

    def goto_tree(self):
        self.ids.content.page = 6

    def game_path_button_callback(self):
        path = diropenbox()
        if not path:
            path = ''

        self.ids.game_add_form_dir.text = path

    def game_launch_path_button_callback(self):
        path = fileopenbox(filetypes=['*.exe', '*.url'], default=self.ids.game_add_form_dir.text + '\\*.exe')
        if not path:
            path = ''

        self.ids.game_add_form_launch.text = path

    def add_game_callback(self):
        os.makedirs('.config', exist_ok=True)

        game_name = self.ids.game_name_input.text
        game_patch_dir = self.ids.game_add_form_dir.text
        game_launch_path = self.ids.url_input.text

        if game_launch_path:
            is_url = True

        else:
            game_launch_path = self.ids.game_add_form_launch.text
            is_url = False

        data = {
            'path': game_patch_dir,
            'launchPath': game_launch_path,
            'isURL': is_url,
        }

        store = JsonStore(GameCollection.CUSTOM_PATHS_PATH)
        store.put(game_name, **data)

        self.cancel_add_game_callback()

    def cancel_add_game_callback(self):
        self.ids.game_name_input.text = ''
        self.ids.game_add_form_dir.text = ''
        self.ids.game_add_form_launch.text = ''
        self.ids.url_input.text = ''
        self.goto_collection()

    def reset_custom_paths(self):
        if os.path.isfile(GameCollection.CUSTOM_PATHS_PATH):
            os.remove(GameCollection.CUSTOM_PATHS_PATH)
            self.info('Purge finished | Deleted all customly added games')

        else:
            self.info('Nothing to delete | No changes have been made to the Game Collection')

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
    store = None

    def __init__(self, **kw):
        super().__init__(**kw)

        if not os.path.isfile('.config/Config.json'):
            self.create_config_store()

        else:
            self.load_store()

    def load_store(self):
        self.store = JsonStore('.config/Config.json')

    def create_config_store(self):
        os.makedirs('.config', exist_ok=True)

        self.load_store()
        self.store.put('Collection', mipmapping=False)

    def mipmap_switch_callback(self, _, enabled):
        info('{}abling mipmapping | Please wait..'.format('En' if enabled else 'Dis'))

        self.store.put('Collection', mipmapping=enabled)
        Clock.schedule_once(lambda *args: self.root.ids.game_collection_view.reload_mipmapping(enabled), .5)


if __name__ == '__main__':
    xtremeupdater = XtremeUpdaterApp()
    xtremeupdater.run()