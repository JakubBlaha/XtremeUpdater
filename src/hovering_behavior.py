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

    def on_hovering(self, *args):
        if self.hovering:
            self.on_enter()
        else:
            self.on_leave()

    def on_enter(self):
        pass

    def on_leave(self):
        pass

class RelativeLayoutHoveringBehavior(HoveringBehavior):
    def on_mouse_pos(self, _, pos):
        x1, y1 = self.to_window(*self.pos)
        x2, y2 = x1 + self.width, y1 + self.height
        mouse_x, mouse_y = pos

        self.hovering = x1 < mouse_x and x2 > mouse_x and y1 < mouse_y and y2 > mouse_y
 