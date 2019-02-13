from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.clock import Clock
from win32gui import GetCursorPos

class WindowDragBehavior(Widget):
    def on_touch_up(self, touch):
        try:
            self.drag_clock.cancel()
        except AttributeError:
            pass

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return

        self.touch_x = touch.x
        self.touch_y = Window.height - touch.y

        self.on_touch_up(None)
        self.drag_clock = Clock.schedule_interval(lambda *args: self.__drag(),
                                                  1 / 60)

    def __drag(self, *args):
        x, y = GetCursorPos()

        x -= self.touch_x
        y -= self.touch_y + 1

        Window.left, Window.top = x, y