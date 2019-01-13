from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.properties import BooleanProperty, ObjectProperty, StringProperty, NumericProperty

import sys, os
sys.path.insert(0, os.path.abspath(
    os.path.join(__file__, os.pardir, os.pardir)))

from behaviors.warning_behavior import WarningBehavior


class CustSwitch(Widget):
    active = BooleanProperty(False)
    command = ObjectProperty()

    # Internal use
    _switch_x_normal = NumericProperty(0)

    def on_active(self, *args):
        Animation(_switch_x_normal=self.active, d=.2, t='out_expo').start(self)

    def on_touch_down(self, touch):
        if not (self.collide_point(*touch.pos)
                and callable(self.command)) or self.disabled:
            return

        if self.command(None, not self.active) is not False:
            self.active = not self.active


class LabelSwitch(CustSwitch, WarningBehavior):
    text = StringProperty()