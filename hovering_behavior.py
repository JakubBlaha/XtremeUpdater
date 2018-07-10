from kivy.core.window import Window
from kivy.properties import BooleanProperty
from kivy.uix.widget import Widget

class HoveringBehavior(Widget):
    hovering = BooleanProperty(False)

    def __init__(self, **kw):
        super().__init__(**kw)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, _, pos):
        self.hovering = super().collide_point(*pos)
 