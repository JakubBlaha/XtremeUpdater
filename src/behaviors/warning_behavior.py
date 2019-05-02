from kivy.event import EventDispatcher
from kivy.properties import StringProperty, NumericProperty, ObjectProperty


def refer_func(fn):
    '''
    Passes the function as an argument to the function itself. Can be used for
    referring itself.
    '''

    def wrapper(*args, **kw):
        return fn(fn, *args, **kw)

    return wrapper


class WarningBehavior(EventDispatcher):
    '''
    Manages `self.warning_level` depending on the `self.command` attribute
    validity.

    Used for `LabelIconButton` and `LabelSwitch` classes.
    '''

    warning_icon = StringProperty('\ue783')
    warning_level = NumericProperty(2)  # TODO -1, custom
    command = ObjectProperty()

    def on_command(self, __, command):  # TODO set to callable
        if not callable(command):
            self.set_warning_level(2)
        else:
            self.set_warning_level(0)

    def set_warning_level(self, level: int):
        self.warning_level = level