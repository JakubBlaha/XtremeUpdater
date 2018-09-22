from kivy.core.window import Window
from kivy.properties import BooleanProperty, DictProperty
from kivy.uix.widget import Widget
from kivy.animation import Animation

class HoveringBehavior(Widget):
    hovering = BooleanProperty(False)
    hovering_attrs = DictProperty()
    _orig_attrs = {}
    anim_kw = DictProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        self.bind_hovering()

    def bind_hovering(self, *args):
        Window.bind(mouse_pos=self.on_mouse_pos)

    def unbind_hovering(self, *args):
        Window.unbind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, _, pos):
        self.hovering = self.collide_point(*self.to_widget(*pos))

    def on_hovering(self, *args):
        if self.hovering:
            self.on_enter()
        else:
            self.on_leave()

    def on_enter(self):
        for key in self.hovering_attrs.keys():
            self._orig_attrs[key] = getattr(self, key)

        Animation(**self.hovering_attrs, **self.anim_kw).start(self)

    def on_leave(self):
        # TODO HOTFIX, AttributeError
        self._orig_attrs = {
            key: value for key, value in self._orig_attrs.items() if hasattr(self, key)
        }

        Animation(**self._orig_attrs, **self.anim_kw).start(self)
 