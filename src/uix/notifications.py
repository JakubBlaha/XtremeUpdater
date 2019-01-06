import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(__file__, os.pardir, os.pardir)))

from kivy.uix.popup import Popup, ModalView
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window

from behaviors.ignoretouch import IgnoreTouchBehavior
# from ..behaviors.ignoretouch import IgnoreTouchBehavior
# TODO: relative imports don't work


class NotifManager:
    _active_notifs = []

    @classmethod
    def add_notif(cls, notif):
        # verify that notif is an actual Notification
        if not isinstance(notif, Notification):
            Logger.error(
                f'NotifManager: Attempted to add a non-notification instance')
            return False

        # add to notification list
        cls._active_notifs.append(notif)

        cls.move_notifs_by_last()

        # open if needed
        if not notif._window:
            notif.open()

        # schedule dismiss
        Clock.schedule_once(notif.dismiss, 3)

    @classmethod
    def move_notifs_by_last(cls):
        last_notif = cls._active_notifs[-1]

        for _notif in cls._active_notifs[:-1]:
            Animation(
                pos_hint={
                    'top': (_notif.pos_hint['top'] * Window.height -
                            last_notif.height - 1) / Window.height
                },
                d=.2,
                t='out_expo').start(_notif)

    @classmethod
    def dismiss_all(cls):
        for notif in cls._active_notifs:
            notif.dismiss()

        cls._active_notifs = []


class Notification(Popup, IgnoreTouchBehavior):
    # TODO make this rather a ModalView
    # TODO add duration parameter

    title_ = StringProperty('Notification')
    message = StringProperty('Example message')
    _decor_size = ListProperty([6, 20])
    _bg_offset = NumericProperty(-200)

    def __init__(self, **kw):
        super().__init__(**kw)

        # Markup the title
        self.children[0].children[2].markup = True

        # is_notif = hasattr(app, 'curr_notif')

        anim = (
            Animation(_decor_size=[self._decor_size[0], 0], d=0) + Animation(
                opacity=1,
                _bg_offset=0,
                _decor_size=self._decor_size,
                d=.5,
                t='out_expo'))
        anim.start(self)

        NotifManager.add_notif(self)

    def dismiss(self, *args):
        anim = Animation(
            opacity=0, _bg_offset=200, _decor_size=[0, 0], d=.5, t='in_expo')
        anim.bind(
            on_complete=lambda *args: super(Notification, self).dismiss())
        anim.start(self)


class WorkingNotif(ModalView, IgnoreTouchBehavior):
    text = StringProperty()

    _highlight_alpha = NumericProperty(.8)

    def open(self, *args, **kw):
        if not kw.get('animation', True):
            self.pos_hint = {'top': 1}
        return super().open(*args, **kw)

    def on_open(self):
        # Come-in animation
        Animation(pos_hint={'top': 1}, d=.5, t='out_expo').start(self)

        # Bg flashing animation
        anim = (Animation(_highlight_alpha=.8, t="out_expo") + Animation(
            _highlight_alpha=0, t="out_expo"))
        anim.repeat = True
        anim.start(self)

    def dismiss(self, *args):
        # Come-out animation
        anim = Animation(
            pos_hint={'top': (Window.height + self.height) / Window.height},
            d=.5,
            t='out_expo')
        anim.bind(
            on_complete=lambda *__: super(WorkingNotif, self).dismiss(args))
        anim.start(self)
