from kivy.lang.builder import Builder
# from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, StringProperty
from kivy.logger import Logger

import sys, os
sys.path.insert(0, os.path.abspath(
    os.path.join(__file__, os.pardir, os.pardir)))

from tweaks import TWEAKS_CLASSES, Tweaks
from uix.switch import LabelSwitch
from uix.button import LabelIconButton

kv = \
'''
#:import theme theme.Theme

<TweaksManager>:
    padding: 10, 40
    spacing: 10
    size_hint_y: None
    height: self.minimum_height
    orientation: 'vertical'

<Group>:
    size_hint_x: 1
    size_hint_y: None
    height: self.minimum_height
    orientation: 'vertical'
    spacing: 10

    Label:
        color: theme.sec
        font_size: 15
        size_hint_y: None
        height: 30
        text_size: self.size
        padding: 0, 2
        text: root.name

        canvas:
            Color:
                rgb: self.color

            Line:
                points: self.x, self.y, self.x + self.width, self.y

    StackLayout:
        id: container
        size_hint: 1, None
        height: self.minimum_height
        spacing: 10
'''

Builder.load_string(kv)


class Group(BoxLayout):
    name = StringProperty()
    color = ListProperty((0, 0, 0, 0))

    def __init__(self, **kw):
        self.name = kw.pop('name', 'Missing category')

        super().__init__(**kw)

    def add(self, wg):
        return self.ids.container.add_widget(wg)


class TweaksManager(BoxLayout):
    tweaks = ListProperty()

    # Internal use
    _tweaks = []
    _groups = []

    def on_tweaks(self, __, tweaks):
        # get added tweaks
        new = [tweak for tweak in tweaks if not tweak in self._tweaks]

        for tweak in new:
            # validate
            if not self._validate_tweak(tweak):
                Logger.error('TweaksManager: Skipped a tweak'
                             )  # TODO which tweak, name attr for tweaks
                continue

            # add widget
            if hasattr(tweak, 'switch'):
                wg = LabelSwitch(
                    text=tweak.text,
                    command=tweak.switch,
                    active=tweak.active,
                    disabled=not tweak.available)
            else:
                wg = LabelIconButton(
                    text_=tweak.text,
                    icon=tweak.icon,
                    command=tweak.apply,
                    disabled=not tweak.available)

            group = self._get_group(tweak.group)
            group.add(wg)

        # update old list
        self._tweaks = tweaks

    def _validate_tweak(self, tweak):
        return type(tweak) in TWEAKS_CLASSES.values()

    def _get_group(self, name):
        for group in self._groups:
            if group.name == name:
                return group

        group = Group(name=name)
        self.add_widget(group)
        self._groups.append(group)
        return group
