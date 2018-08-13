from kivy.core.window import Window
from kivy.properties import BooleanProperty
from kivy.uix.widget import Widget

class HoveringBehavior(Widget):
    hovering = BooleanProperty(False)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.bind_hovering()

    def bind_hovering(self):
        Window.bind(mouse_pos=self.on_mouse_pos)

    def unbind_hovering(self):
        Window.unbind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, _, pos):
        self.hovering = super().collide_point(*self.to_widget(*pos))

    def on_hovering(self, *args):
        if self.hovering:
            self.on_enter()
        else:
            self.on_leave()

    def on_enter(self):
        pass

    def on_leave(self):
        pass
 