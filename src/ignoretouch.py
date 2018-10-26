class IgnoreTouchBehavior:
    def __init_subclass__(cls, *args, **kw):
        super().__init_subclass__(*args, **kw)

        orig_init = cls.__init__

        def new_init(self, **kw):
            orig_init(self, **kw)
            self.on_touch_down = self.on_touch_down_
            self.on_touch_up = self.on_touch_up_
            self.on_touch_move = self.on_touch_move_

        cls.__init__ = new_init

    def on_touch_down_(*args):
        pass

    def on_touch_up_(*args):
        pass

    def on_touch_move_(*args):
        pass
