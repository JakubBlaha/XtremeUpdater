import win32gui
from tkinter.filedialog import askdirectory
from threading import Thread
from tkinter import Tk
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
Config.set('input', 'mouse', 'mouse, disable_multitouch')

from kivy.app import App
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.core.window import Window
Window.clearcolor = sec

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.pagelayout import PageLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.graphics import Color, Rectangle
from kivy.properties import BooleanProperty, StringProperty, NumericProperty, ObjectProperty, ListProperty


def prepare_rv_dlls(path):
    filenames = os.listdir(path)
    dll_names = [
        filename for filename in filenames
        if os.path.splitext(filename)[1] == '.dll'
    ]
    return [{'text': dll} for dll in dll_names]


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''


class DllRecycleView(RecycleView):
    def select_all(self):
        pass
    
    def deselect_all(self):
        pass

    def get_selection(self):
        pass


class SelectableLabel(RecycleDataViewBehavior, Label):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected


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

    def __init__(self, **kwargs):
        super(Button, self).__init__(**kwargs)

        self.anim_in = Animation(color=prim, d=.1)
        self.anim_out = Animation(color=self.color, d=.1)

        Window.bind(mouse_pos=self.on_motion)
        self.bind(hovering=self._hovering_callback)

    def on_motion(self, _, pos):
        self.hovering = self.collide_point(*pos)

    def _hovering_callback(self, _, is_hovering):
        if is_hovering:
            self.on_enter()
        else:
            self.on_leave()

    def on_enter(self):
        self.anim_in.start(self)

    def on_leave(self):
        self.anim_out.start(self)


class HeaderLabel(WindowDragBehavior, Label):
    pass


class PageSwitchBehavior():
    page_index = NumericProperty(None)

    def on_release(self):
        if not isinstance(self.page_index, int):
            raise AttributeError("Bad value for attribute 'page_index'")

        self.parent.active = self.page_index


class NavigationButton(PageSwitchBehavior, CustButton):
    pass


class IconNavigationButton(PageSwitchBehavior):
    pass


class Navigation(BoxLayout):
    active = NumericProperty(0)
    __last_highlight = 0
    page_layout = ObjectProperty(None)
    tabs = ListProperty()
    '''Prepared animations'''
    anim_nohighlight = Animation(background_color=dark, d=.1)
    anim_highlight = Animation(background_color=prim, color=fg, d=.1)

    def __init__(self, **kwargs):
        super(Navigation, self).__init__(**kwargs)

        self.bind(active=self._active_callback)
        self.bind(children=self._children_callback)

    def _children_callback(self, _, children):
        self.tabs = [
            child for child in children if isinstance(child, NavigationButton)
        ][::-1]

        self.anim_highlight.start(self.tabs[self.__last_highlight])

    def _active_callback(self, *args):
        if not isinstance(self.page_layout, PageLayout):
            raise AttributeError("Bad value for attribute 'page_layout'")

        self.anim_nohighlight.start(self.tabs[self.__last_highlight])
        self.anim_highlight.start(self.tabs[self.active])

        self.page_layout.page = self.active
        self.__last_highlight = self.active


class Content(PageLayout):
    def __init__(self, **kwargs):
        super(Content, self).__init__(**kwargs)

        self.bind(page=self._page_callback)

    def _page_callback(self, _, value):
        app.root.ids.navigation.active = value


class PlaceHolder(Label):
    shown_text = StringProperty('Coming soon')
    icon = StringProperty('\ue946')
    rendered_text = StringProperty()

    def __init__(self, **kwargs):
        super(PlaceHolder, self).__init__(**kwargs)

        self.bind(shown_text=self.render_text, icon=self.render_text)

    def render_text(self, *args):
        self.rendered_text = f'[size=72][font=fnt/segmdl2.ttf]{self.icon}[/font][/size]\n{self.shown_text}'


class OverwriteLabel(FloatLayout):
    icon = StringProperty()
    text = StringProperty()
    wg = ObjectProperty()

    def __init__(self, **kwargs):
        self.icon = kwargs.get('icon', '')
        self.text = kwargs.get('text', '')
        self.wg = kwargs.get('wg', None)

        super(OverwriteLabel, self).__init__()

        self.wg.add_widget(self)

        anim = Animation(opacity=1, d=.2)
        anim.start(self)

    def dismiss(self):
        anim = Animation(opacity=0, d=.2)
        anim.bind(on_complete=lambda *args: self.wg.remove_widget(self))
        anim.start(self)


class RootLayout(BoxLayout):
    def load_directory(self):
        w = Tk()
        w.withdraw()
        path = askdirectory()
        w.destroy()
        self.ids.content_updater_path_info.text = path
        self.load_dll_view_data(path)

    def load_dll_view_data(self, path):
        self.ids.dll_view.data = prepare_rv_dlls(path)
        self.ids.dll_view_holder.overdrawer.dismiss()
        self.ids.dll_view.select_all()


class XtremeUpdaterApp(App):
    def build(self):
        return RootLayout()

    def on_start(self):
        self.root.ids.navigation.active = 0
        self.root.ids.dll_view_holder.overdrawer = OverwriteLabel(
            wg=self.root.ids.dll_view_holder,
            icon='\uf12b',
            text='Select a directory first')


if __name__ == '__main__':
    app = XtremeUpdaterApp()
    app.run()