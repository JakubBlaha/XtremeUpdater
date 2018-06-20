import win32gui
from tkinter.filedialog import askdirectory
from threading import Thread
from easygui import diropenbox
import urllib.request
from kivy.network.urlrequest import UrlRequest
from bs4 import BeautifulSoup
from shutil import copy
import os
from theme import *

import kivy
kivy.require('1.10.0')

from kivy import Config
Config.set('graphics', 'multisamples', 0)
Config.set('graphics', 'width', 800)
Config.set('graphics', 'height', 450)
Config.set('graphics', 'borderless', 1)
Config.set('graphics', 'resizable', 0)
# Config.set('input', 'mouse', 'mouse, disable_multitouch')

from kivy.app import App
from kivy.clock import Clock
from kivy.clock import mainthread
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.factory import Factory
Window.clearcolor = sec

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.pagelayout import PageLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.recycleview import RecycleView
from kivy.properties import BooleanProperty, StringProperty, NumericProperty, ObjectProperty, ListProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.layout import CompoundSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior


def local_dlls(path):
    return [
        item for item in os.listdir(path)
        if os.path.splitext(item)[1] == '.dll'
    ]


def get_data(url):
    return urllib.request.urlopen(url).read()


def info(text):
    App.get_running_app().root.info(text)


class DllUpdater:
    URL = "https://github.com/XtremeWare/XtremeUpdater/tree/master/dll/"
    RAW_URL = "https://github.com/XtremeWare/XtremeUpdater/raw/master/dll/"
    BACKUP_DIR = ".backup/"
    _available_dlls = []

    @staticmethod
    def load_available_dlls():
        try:
            html = get_data(DllUpdater.URL)

        except:
            raise SyncError

        else:
            soup = BeautifulSoup(html, 'html.parser')
            for a in soup.find_all('a', {'class': 'js-navigation-open'}):
                if a.parent.parent.get('class')[0] == 'content':
                    DllUpdater._available_dlls.append(a.text)

            if DllUpdater._available_dlls:
                info(
                    'We have found some dll updates | Please select your updates'
                )
            else:
                info(
                    'We have not found any dll updates | Try selecting another directory'
                )

            return True

    @staticmethod
    def available_dlls():
        'referencing'
        if not DllUpdater._available_dlls:
            DllUpdater.load_available_dlls()

        return DllUpdater._available_dlls

    @staticmethod
    def _mkbackupdir():
        if not os.path.exists(DllUpdater.BACKUP_DIR):
            os.mkdir(DllUpdater.BACKUP_DIR)

    @staticmethod
    def _download_dll(dllname):
        _adress = os.path.join(DllUpdater.RAW_URL, dllname)
        _data = get_data(_adress)

        return _data

    @staticmethod
    def _backup_dlls(path, dlls):
        _to_backup = [item for item in os.listdir(path) if item in dlls]
        for dll in _to_backup:
            dst = os.path.realpath(
                os.path.join(DllUpdater.BACKUP_DIR,
                             os.path.splitdrive(path)[1][1:]))

            if not os.path.exists(dst):
                os.makedirs(dst)

            copy(os.path.join(path, dll), dst)

    @staticmethod
    def _overwrite_dll(path, data):
        with open(path, 'wb') as f:
            f.write(data)

    @staticmethod
    def update_dlls(path, dlls):
        dll_num = len(dlls)

        DllUpdater._mkbackupdir()

        app = App.get_running_app()
        app.root.info("Backing up dlls | Please wait..")
        DllUpdater._backup_dlls(path, dlls)

        for index, dll in enumerate(dlls):
            app.root.info(
                f"Downloading {dll} ({index + 1} of {dll_num}) | Please wait.."
            )
            data = DllUpdater._download_dll(dll)
            DllUpdater._overwrite_dll(os.path.join(path, dll), data)

        app.root.info("We are done | Let's speed up your system now")

    @staticmethod
    def restore_dlls(path, dlls):
        app = App.get_running_app()
        app.root.info("Restoring | Please wait..")

        dll_num = len(dlls)
        bck_path = os.path.abspath(
            os.path.join(DllUpdater.BACKUP_DIR,
                         os.path.splitdrive(path)[1][1:]))

        _restored = 0
        for index, dll in enumerate(dlls):
            i = index + 1

            backed_dll_path = os.path.join(bck_path, dll)
            try:
                copy(backed_dll_path, path)
            except:
                pass
            else:
                _restored += 1

        app.root.info(
            f"Restoring done | Restored {_restored} of {dll_num} dlls")

    @staticmethod
    def available_restore(path):
        bck_path = os.path.abspath(os.path.join(DllUpdater.BACKUP_DIR, path))

        return os.listdir(bck_path)


class WindowDragBehavior(Widget):
    def on_touch_up(self, touch):
        if hasattr(self, 'drag_clock'):
            self.drag_clock.cancel()

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return

        self.touch_x = touch.x
        self.touch_y = Window.height - touch.y

        self.drag_clock = Clock.schedule_interval(lambda *args: self.__drag(),
                                                  1 / 60)

    def __drag(self, *args):
        x, y = win32gui.GetCursorPos()

        x -= self.touch_x
        y -= self.touch_y

        Window.left, Window.top = x, y


class CustButton(Button):
    hovering = BooleanProperty(False)
    anim_in = Animation(color=prim, d=.1)
    anim_disabled = Animation(opacity=0, d=.1)
    anim_normal = Animation(opacity=1, d=.1)

    def __init__(self, **kwargs):
        super(Button, self).__init__(**kwargs)

        self.anim_out = Animation(color=self.color, d=.1)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, _, pos):
        self.hovering = self.collide_point(*pos)

    def on_hovering(self, _, is_hovering):
        if is_hovering:
            self.on_enter()
        else:
            self.on_leave()

    def on_enter(self):
        if not self.disabled:
            self.anim_in.start(self)

    def on_leave(self):
        if not self.disabled:
            self.anim_out.start(self)

    def on_disabled(self, custbutton, is_disabled):
        if is_disabled:
            self.anim_disabled.start(self)
        else:
            self.anim_normal.start(self)


class PageSwitchBehavior():
    page_index = NumericProperty(None)

    def on_release(self):
        print('called')
        if not isinstance(self.page_index, int):
            raise AttributeError("Bad value for attribute 'page_index'")

        self.parent.active = self.page_index


class NavigationButton(PageSwitchBehavior, CustButton):
    pass


class Navigation(BoxLayout):
    active = NumericProperty(0)
    __last_highlight = 0
    page_layout = ObjectProperty(None)
    tabs = ListProperty()

    anim_nohighlight = Animation(background_color=dark, d=.1)
    anim_highlight = Animation(background_color=prim, color=fg, d=.1)

    def on_children(self, Navigation, children):
        self.tabs = [
            child for child in children if isinstance(child, NavigationButton)
        ][::-1]

        self.anim_highlight.start(self.tabs[self.active])

    def on_active(self, *args):
        if not isinstance(self.page_layout, PageLayout):
            raise AttributeError("Bad value for attribute 'page_layout'")

        self.anim_nohighlight.start(self.tabs[self.__last_highlight])
        self.anim_highlight.start(self.tabs[self.active])

        self.page_layout.page = self.active
        self.__last_highlight = self.active


class Content(PageLayout):
    def on_page(self, Content, value):
        self.parent.active = value


class PlaceHolder(Label):
    message = StringProperty('Coming soon')
    icon = StringProperty('\ue946')


class OverdrawLabel(FloatLayout):
    icon = StringProperty()
    text = StringProperty()
    secondary_text = StringProperty()
    template = '[size=72][font=fnt/segmdl2.ttf]{}[/font][/size]\n{}[size=14]{}[/size]'
    wg = ObjectProperty()

    @mainthread
    def __init__(self, wg, icon='\ue943', text='', secondary_text='', **kw):
        self.icon = icon
        self.text = 'Oops..' if not text else text
        self.secondary_text = 'Someone forgot to put code here' if not text else secondary_text
        if self.secondary_text:
            self.secondary_text = '\n' + self.secondary_text

        self.wg = wg

        super(OverdrawLabel, self).__init__(**kw)

        if hasattr(wg, 'overdrawer') and isinstance(wg.overdrawer,
                                                    OverdrawLabel):
            wg.overdrawer.dismiss()

        wg.overdrawer = self
        wg.add_widget(self)

        self._display()

    @mainthread
    def _display(self):
        Animation(opacity=1, d=.2).start(self)

    @mainthread
    def kill(self):
        self.wg.remove_widget(self)

    @mainthread
    def dismiss(self, *args):
        Animation(opacity=0, d=.2).start(self)

    @mainthread
    def update(self, **kw):
        def on_complete(*args):
            self.icon = kw.get('icon', self.icon)
            self.text = kw.get('text', self.text)
            self.secondary_text = '\n' + kw.get('secondary_text', self.secondary_text).strip()

            Animation(color=prim, d=.2).start(self.ids.label)

        anim = Animation(color=sec, d=.2)
        anim.bind(on_complete=on_complete)
        anim.start(self.ids.label)

        self._display()


from kivy.uix.listview import ListItemButton
class DllViewItem(ListItemButton):
    selectable = BooleanProperty(True)

    def on_is_selected(self, DllViewItem, is_selected):
        if is_selected and self.selectable:
            self.select()
        else:
            self.deselect()


from kivy.adapters.listadapter import ListAdapter
class DllViewAdapter(ListAdapter):
    def on_data(self, *args):
        if not self.data:
            return

        available_dlls = DllUpdater.available_dlls()
        self.data = [{**item, 'selectable': item['text'] in available_dlls} for item in self.data]

        self.select_all()

    def on_selection_change(self, *args):
        App.get_running_app().root.set_dll_buttons_state(self.selection)

    def select_all(self):
        # TODO
        pass

    def deselect_all(self):
        # TODO
        pass


class RootLayout(BoxLayout):
    def set_dll_buttons_state(self, enabled):
        # TODO animation
        self.ids.restore_button.disabled = not enabled
        self.ids.update_button.disabled = not enabled

    def load_directory(self):
        info('Select a directory now | Waiting..')

        path = diropenbox()

        if not os.path.isdir(path):
            info('Seems like an invalid directory | Try again')
            return

        self.ids.content_updater_path_info.text = path
        self.load_dll_view_data(path)

    def load_dll_view_data(self, path):
        self.set_dll_buttons_state(False)

        if not local_dlls(path):
            self.ids.dll_view.overdrawer.update(
                icon='\ue783', text='No dlls found here')
            info(
                'We have not found any dlls in this directory | Try selecting another one'
            )

            return

        self.ids.dll_view.overdrawer.update(
            icon='\uede4', text='Looking for dlls..', secondary_text="It shouldn't take too long")

        DllUpdater.load_available_dlls()

        self.ids.dll_view.adapter.data = [{'text': item} for item in local_dlls(path)]
        self.ids.dll_view.overdrawer.dismiss()


    def update_callback(self):
        draw = OverdrawLabel(self.ids.dll_view, '\ue896',
                             'Updating dlls..')

        dlls = [item.text for item in self.ids.dll_view.adapter.selection]

        print(dlls)

        def thread():
            DllUpdater.update_dlls(self.ids.content_updater_path_info.text,
                                   dlls)
            draw.dismiss()

        Thread(target=thread).start()

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
    def build(self):
        return RootLayout()

    def on_start(self):
        OverdrawLabel(self.root.ids.dll_view, '\uf12b',
                      'First, select a directory', 'Press the folder button')
        Clock.schedule_once(
            lambda *args: self.root.info('Select a directory | Click the folder button'),
            2)


if __name__ == '__main__':
    app = XtremeUpdaterApp()
    app.run()