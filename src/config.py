import os
import yaml
from kivy.logger import Logger


class Conf:
    __store = {}
    __path = ''

    def __init__(self, path, defaults):
        object.__setattr__(self, '__path', path)

        os.makedirs(os.path.dirname(path), exist_ok=True)

        try:
            with open(path, 'r') as config:
                object.__setattr__(self, '__store', {
                    **defaults,
                    **yaml.load(config)
                })
        except FileNotFoundError:
            Logger.warning('Config file not found!')
            Logger.info(
                f'Creating config file at {path} with values {defaults}..'
            )

            with open(path, 'w') as f:
                yaml.dump(defaults, f)

            object.__setattr__(self, '__store', defaults)

    def __setattr__(self, name, value):
        object.__getattribute__(self, '__store')[name] = value
        self.__dump_to_file()

    def __getattr__(self, name):
        try:
            return object.__getattribute__(self, '__store')[name]
        except KeyError:
            raise AttributeError

    def __dump_to_file(self):
        with open(object.__getattribute__(self, '__path'), 'w') as conf:
            conf.write(yaml.dump(object.__getattribute__(self, '__store')))
