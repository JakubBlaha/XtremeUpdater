from kivy.animation import Animation
from kivy.app import App
from kivy.uix.button import Button
from kivy.properties import StringProperty, NumericProperty
from kivy.metrics import sp

import sys, os
sys.path.insert(0, os.path.abspath(
    os.path.join(__file__, os.pardir, os.pardir)))

from hovering import HoveringBehavior
from behaviors.warning_behavior import WarningBehavior


class CustButton(Button, HoveringBehavior):
    _orig_font_opacity = 1

    def __init__(self, **kw):
        super().__init__(**kw)
        self.orig_font_opacity = self.color[3]

    def on_disabled(self, *args):
        if self.disabled:
            self._orig_font_opacity = self.color[3]
            Animation(color=self.color[:3] + [.1], d=.1).start(self)
            if self.hovering:
                self.on_leave()

        else:
            Animation(
                color=self.color[:3] + [self._orig_font_opacity],
                d=.1).start(self)
            if self.hovering:
                self.on_enter()


class BackgroundedButton(CustButton):
    pass


class IconButton(CustButton):
    icon = StringProperty()


class LabelIconButton(IconButton, WarningBehavior):
    text_ = StringProperty()  # Label text
    font_size_ = NumericProperty(sp(15))  # Label font_size
    opacity_ = NumericProperty(1)  # Label opacity

    _btn_width = NumericProperty()


class ExpandableLabelIconButton(LabelIconButton):
    def on_text_(self, __, text):
        if not App.get_running_app().built: # Do not waste resources
            Animation(
                _btn_width=self.height if text else self.width,
                opacity_=1 if text else 0,
                d=.5,
                t='out_expo').start(self)
        else:
            self._btn_width = self.height if text else self.width
            self.opacity_ = 1 if text else 0
