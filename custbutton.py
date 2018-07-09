from kivy.uix.button import Button
from kivy.properties import StringProperty, ListProperty
from kivy.animation import Animation
from kivy.clock import Clock
from hovering_behavior import HoveringBehavior
from theme import *


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

    def on_hovering(self, _, is_hovering):
        if is_hovering:
            self.on_enter()
        else:
            self.on_leave()

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

    def on_disabled(self, _, is_disabled):
        super().on_disabled(_, is_disabled)

        if is_disabled:
            Animation(opacity=0, d=.1).start(self)

        else:
            Animation(opacity=1, d=.1).start(self)