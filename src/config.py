import os
import yaml
from kivy.logger import Logger


class ConfigMeta(type):
    path = ''
    _store = {'proxy_ref': None}

    def reload_store(cls):
        # Ensure config file
        if not os.path.isfile(cls.path):
            os.makedirs(os.path.dirname(cls.path), exist_ok=True)
            try:
                open(cls.path, 'w').close()
            except OSError:
                Logger.error(
                    f'Config: Failed to create the config file in {cls.path}. Is direcotry: {os.path.isdir(cls.path)}'
                )
            return

        # Load config file
        with open(cls.path) as f:
            data = yaml.load(f)
        if not type(data) == dict:
            return
        cls._store.update(data)
        Logger.info(f'Config: Reloaded store from {cls.path} | {cls._store}')

    def dump_to_file(cls):
        try:
            with open(cls.path, 'w') as f:
                yaml.dump(cls._store, f)
        except OSError:
            Logger.error(
                f'Config: Failed to dump the config {cls._store} to {cls.path}'
            )
        else:
            Logger.info(f'Config: Dumped config to {cls.path} | {cls._store}')

    def __getattr__(cls, name):
        return cls._store[name]

    def __setattr__(cls, name, value):
        try:
            cls.name
        except KeyError:
            cls._store[name] = value
            Logger.info(f'Config: Set `{name}` to `{value}`')
        else:
            return type.__setattr__(cls, name, value)

    def get(cls, name, default):
        return cls._store.get(name, default)


class Config(metaclass=ConfigMeta):
    path = '.config/config.yaml'