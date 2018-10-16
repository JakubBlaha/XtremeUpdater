from kivy.properties import BooleanProperty, DictProperty
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.event import EventDispatcher
from kivy.factory import Factory
from kivy.clock import Clock


class HoveringBehavior(EventDispatcher):
    hovering = BooleanProperty(False)
    hovering_attrs = DictProperty()
    anim_kw = DictProperty()
    _orig_attrs = {}

    def __init__(self, **kw):
        self.register_event_type('on_enter')
        self.register_event_type('on_leave')

        super().__init__(**kw)

        self.bind_hovering()

    def bind_hovering(self, *args):
        Window.bind(mouse_pos=self.on_mouse_pos)

    def unbind_hovering(self, *args):
        Window.unbind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, _, pos):
        if not self.get_root_window():
            return

        self.hovering = self.collide_point(*self.to_widget(*pos))

    def on_hovering(self, __, hovering):
        self.dispatch('on_enter' if hovering else 'on_leave')

    def update_orig_attrs(self, *args):
        self._orig_attrs = {
            key: getattr(self, key)
            for key in self.hovering_attrs.keys()
        }

    def on_enter(self):
        if getattr(self, 'disabled', False):
            return

        if not self._orig_attrs:
            self.update_orig_attrs()

        try:
            self.on_leave_anim.stop(self)
        except AttributeError:
            pass

        self.on_enter_anim = Animation(**self.hovering_attrs, **self.anim_kw)
        self.on_enter_anim.start(self)

    def on_leave(self):
        try:
            self.on_enter_anim.stop(self)
        except AttributeError:
            pass

        self.on_leave_anim = Animation(**self._orig_attrs, **self.anim_kw)
        self.on_leave_anim.start(self)

    def on_hovering_attrs(self, *args):
        self.on_hovering(self, self.hovering)


Factory.register('HoveringBehavior', HoveringBehavior)
