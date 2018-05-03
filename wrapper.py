def new_thread(fn):
    def wrapper(*args, **kwargs):
        from _thread import start_new
        start_new(fn, args, kwargs)

    return wrapper