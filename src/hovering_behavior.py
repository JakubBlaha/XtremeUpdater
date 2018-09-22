from kivy.properties import BooleanProperty, DictProperty
from kivy.animation import Animation
from kivy.core.window import Window


class HoveringBehavior():
    hovering = BooleanProperty(False)
    hovering_attrs = DictProperty()
    anim_kw = DictProperty()
    _orig_attrs = {}

    def __init__(self, **kw):
        self.bind_hovering()

    def bind_hovering(self, *args):
        Window.bind(mouse_pos=self.on_mouse_pos)

    def unbind_hovering(self, *args):
        Window.unbind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, _, pos):
        if not self.get_root_window():
            return

        self.hovering = self.collide_point(*self.to_widget(*pos))

    def on_hovering(self, *args):
        if self.hovering:
            self.on_enter()
        else:
            self.on_leave()

    def update_orig_attrs(self, *args):
        for key in self.hovering_attrs.keys():
            self._orig_attrs[key] = getattr(self, key)

    def on_enter(self):
        if not self._orig_attrs:
            self.update_orig_attrs()
        try:
            self.on_leave_anim.stop(self)
        except AttributeError:
            pass
        self.on_enter_anim = Animation(**self.hovering_attrs, **self.anim_kw)
        self.on_enter_anim.start(self)

    def on_leave(self):
        # TODO HOTFIX, AttributeError
        # self._orig_attrs = {
        #     key: value for key, value in self._orig_attrs.items() if hasattr(self, key)
        # }
        try:
            self.on_enter_anim.stop(self)
        except AttributeError:
            pass
        self.on_leave_anim = Animation(**self._orig_attrs, **self.anim_kw)
        self.on_leave_anim.start(self)
