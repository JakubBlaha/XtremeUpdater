import win32gui
from threading import Thread
from easygui import diropenbox
import urllib.request
from bs4 import BeautifulSoup
from shutil import copy
import os

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
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.properties import BooleanProperty, StringProperty, NumericProperty, ObjectProperty, ListProperty
from kivy.adapters.listadapter import ListAdapter
from kivy.uix.listview import ListItemButton
from kivy.uix.switch import Switch


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
    _available_dlls = []
    succeed = BooleanProperty(True)

    @classmethod
    def load_available_dlls(cls):
        try:
            html = get_data(cls.URL)

        except:
            cls.succeed = False
            app().refresh_button_active = True

            info('Syncing failed | Please try again')
            app().root.ids.dll_view.overdrawer.update(
                icon='\uea6a', text='Error when syncing')

            return False

        else:
            cls.succeed = True
            app().refresh_button_active = False

            soup = BeautifulSoup(html, 'html.parser')
            for a in soup.find_all('a', {'class': 'js-navigation-open'}):
                if a.parent.parent.get('class')[0] == 'content':
                    cls._available_dlls.append(a.text)

            if cls._available_dlls:
                info(
                    'We have found some dll updates | Please select your updates'
                )
            else:
                info(
                    'We have not found any dll updates | Try selecting another directory'
                )

            return True

    @classmethod
    def available_dlls(cls):
        if not cls._available_dlls:
            cls.load_available_dlls()

        if not cls.succeed:
            return False

        return cls._available_dlls

    @classmethod
    def _mkbackupdir(cls):
        if not os.path.exists(cls.BACKUP_DIR):
            os.mkdir(cls.BACKUP_DIR)

    @classmethod
    def _download_dll(cls, dllname):
        _adress = os.path.join(cls.RAW_URL, dllname)
        _data = get_data(_adress)

        return _data

    @classmethod
    def _backup_dlls(cls, path, dlls):
        _to_backup = [item for item in os.listdir(path) if item in dlls]
        for dll in _to_backup:
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

        cls._mkbackupdir()

        info("Backing up dlls | Please wait..")
        cls._backup_dlls(path, dlls)

        try:
            for index, dll in enumerate(dlls):
                info(
                    f"Downloading {dll} ({index + 1} of {dll_num}) | Please wait.."
                )
                data = cls._download_dll(dll)
                cls._overwrite_dll(os.path.join(path, dll), data)
        except:
            info("Couldn't download updated dll | Please try again")
            app().root.ids.dll_view.overdrawer.update(
                icon='\uea39', text='Dll download failed')

        else:
            info("We are done | Let's speed up your system now")
            app().root.ids.dll_view.overdrawer.update(
                icon='\ue930', text='Completed')

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
    anim_in = Animation(color=prim, background_color=disabled, d=.1)
    anim_disabled = Animation(opacity=0, d=.1)
    anim_normal = Animation(opacity=1, d=.1)

    def __init__(self, **kw):
        super().__init__(**kw)

        Clock.schedule_once(self._update_anim_out, 0)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def _update_anim_out(self, *args):
        self.anim_out = Animation(
            color=self.color, background_color=self.background_color, d=.1)

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

    def nohighghlight(self):
        self.__active = False
        self.anim_nohighlight.start(self)

    def on_leave(self, *args):
        if not self.__active:
            super().on_leave()

    def on_enter(self, *args):
        if not self.__active:
            super().on_enter()


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
    def on_page(self, Content, value):
        self.parent.active = value


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
        self.icon = icon
        self.text = 'Oops..' if not text else text
        self.wg = wg

        super().__init__(**kw)

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

            Animation(color=prim, d=.2).start(self.ids.label)

        anim = Animation(color=sec, d=.2)
        anim.bind(on_complete=on_complete)
        anim.start(self.ids.label)

        self._display()


class DllViewItem(ListItemButton):
    selectable = BooleanProperty(True)

    def on_is_selected(self, DllViewItem, is_selected):
        if is_selected and self.selectable:
            self.select()
        else:
            self.deselect()


class DllViewAdapter(ListAdapter):
    def on_data(self, *args):
        if not self.data:
            return

        available_dlls = DllUpdater.available_dlls()
        if available_dlls == False:
            self.data = []

        self.data = [{
            **item, 'selectable': item['text'] in available_dlls
        } for item in self.data]

        app().root.ids.invert_selection_button.disabled = not self.data

    def on_selection_change(self, *args):
        app().root.set_dll_buttons_state(self.selection)

    def get_views(self, first=0, last=None) -> list:
        last = last if last is not None else len(self.data)

        # TODO indexing is kinda messed up

        return [
            self.get_view(index)
            for index, item in enumerate(self.data[first:last])
        ]

    def invert_selection(self):
        def callback(*args):
            self.select_list(self.get_views())

        Clock.schedule_once(callback, 0)


# EXPERIMENTAL
class CustSwitch(Switch):
    on = ObjectProperty()
    off = ObjectProperty()
    condition = ObjectProperty()
    _no_trigger_active = False

    def on_active(self, _, active):
        if self._no_trigger_active:
            return

        if active:
            self.on()

        else:
            self.off()

        self.on_condition(None, self.condition)

    def on_condition(self, _, condition):
        self._no_trigger_active = True
        self.active = condition()
        self._no_trigger_active = False


class RootLayout(BoxLayout):
    def set_dll_buttons_state(self, enabled):
        self.ids.restore_button.disabled = not enabled
        self.ids.update_button.disabled = not enabled

    @new_thread
    def load_directory(self):
        info('Select a directory now | Waiting..')
        path = diropenbox()
        self.ids.content_updater_path_info.text = path
        self.load_dll_view_data(path)

    @new_thread
    def load_dll_view_data(self, path):
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

        self.ids.dll_view.overdrawer.update(
            icon='\uede4',
            text='Looking for dlls..',
            secondary_text="It shouldn't take too long")

        self.ids.dll_view.adapter.data = [{
            'text': item
        } for item in local_dlls(path)]
        self.ids.dll_view.overdrawer.dismiss()

        self.ids.dll_view.adapter.invert_selection()

    def update_callback(self):
        self.set_dll_buttons_state(False)
        draw = OverdrawLabel(self.ids.dll_view, '\ue896', 'Updating dlls..')

        dlls = [item.text for item in self.ids.dll_view.adapter.selection]

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