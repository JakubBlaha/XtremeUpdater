import os
import shutil
import platform
from kivy.app import App
from kivy.factory import Factory
from tempfile import gettempdir
from humanize import naturalsize
from winreg import *
from main import IS_ADMIN, silent_exc, notify_restart, theme

APP = App.get_running_app()

if platform.machine().endswith('64'):
    VIEW_FLAG = KEY_WOW64_64KEY
else:
    VIEW_FLAG = KEY_WOW64_32KEY


def get_size(path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            path = os.path.join(dirpath, f)
            total_size += os.path.getsize(path)

    return total_size


class Tweaks:
    @staticmethod
    def clear_temps():
        tmp_dir = gettempdir()
        init_size = get_size(tmp_dir)

        shutil.rmtree(tmp_dir, ignore_errors=True)

        finish_size = get_size(tmp_dir)
        freed_size = init_size - finish_size

        APP.root.bar.ping()
        Factory.Notification(
            title_=f'Freed up [color=5f5]{naturalsize(freed_size)}[/color]',
            message=
            f'Before: {naturalsize(init_size)}    After: {naturalsize(finish_size)}'
        ).open()

    @staticmethod
    def is_dvr():
        key = OpenKeyEx(HKEY_CURRENT_USER, r'System\GameConfigStore')
        GameDVR_enabled = QueryValueEx(key, 'GameDVR_enabled')[0]

        try:
            key = OpenKeyEx(HKEY_LOCAL_MACHINE,
                            r'SOFTWARE\Policies\Microsoft\Windows\GameDVR')
            AllowGameDVR = QueryValueEx(key, 'AllowGameDVR')[0]

        except (OSError, FileNotFoundError):
            AllowGameDVR = 1

        return GameDVR_enabled or AllowGameDVR

    @staticmethod
    @silent_exc
    @notify_restart
    def switch_dvr(_, enabled):
        key = OpenKeyEx(HKEY_CURRENT_USER, r'System\GameConfigStore', 0,
                        KEY_SET_VALUE)
        SetValueEx(key, 'GameDVR_enabled', None, REG_DWORD, enabled)

        key = OpenKeyEx(HKEY_LOCAL_MACHINE,
                        r'SOFTWARE\Policies\Microsoft\Windows\GameDVR', 0,
                        KEY_SET_VALUE)
        SetValueEx(key, 'AllowGameDVR', None, REG_DWORD, enabled)

    @staticmethod
    def fth_value():
        try:
            key = OpenKey(
                HKEY_LOCAL_MACHINE,
                r'SOFTWARE\Microsoft\FTH\State',
                access=KEY_READ | VIEW_FLAG)
        except OSError:
            return False

        try:
            EnumValue(key, 0)
        except OSError:
            return False
        else:
            return True

    @staticmethod
    @silent_exc
    @notify_restart
    def clear_fth():
        APP.root.ids.clear_fth_btn.disabled = True

        key = OpenKey(
            HKEY_LOCAL_MACHINE,
            r'SOFTWARE\Microsoft\FTH\State',
            access=KEY_WRITE | KEY_READ | VIEW_FLAG)
        while True:
            try:
                name = EnumValue(key, 0)[0]
            except OSError:
                break
            else:
                DeleteValue(key, name)

    @staticmethod
    def is_fth():
        try:
            key = OpenKey(
                HKEY_LOCAL_MACHINE,
                r'SOFTWARE\Microsoft\FTH',
                access=KEY_READ | VIEW_FLAG)
        except Exception:
            return False
        else:
            return QueryValueEx(key, 'Enabled')[0]

    @staticmethod
    @silent_exc
    @notify_restart
    def switch_fth(__, enabled):
        key = OpenKey(
            HKEY_LOCAL_MACHINE,
            r'SOFTWARE\Microsoft\FTH',
            access=KEY_WRITE | VIEW_FLAG)
        SetValueEx(key, 'Enabled', None, REG_DWORD, enabled)


# TODO clear the old code
# NEW API
from kivy.logger import Logger
import ctypes
from dataclasses import dataclass, field
import sys
import traceback

ARCH_FLAG = (KEY_WOW64_64KEY
             if platform.machine().endswith('64') else KEY_WOW64_32KEY)


def fstring(string):
    ''' Returns a text where code snippets are replaced with actual values. '''
    return eval(f'f"{string}"')


@dataclass
class TweakBase:
    '''
    Base for the tweak classes. Tweak can be instantiated with json
    as follows.
    ```
    {
        "tweak_class": "TweakBase",
        "apply_notif": {
            "title": "Applied",
            "message": "Tweak has been applied."
        }
        "detach_notif": {
            "title": "Disabled",
            "message": "Tweak has been disabled."
        }
        "show_failure": False,
        "admin_required": True,
        "group": "Test group"
    }
    ```
    `yaml` format can be used for instead of `json` in every subclass.

    Attributes:
        `type_` - Will contain the tweak type whenever
        the instance is constructed from a json file.

        `text` - The text that will be used as the tweak title.

        `group` - The group text that will be shown alongside with the tweak
        widget.

        `apply_notif` - A dictionary containing `title` and `message` keys for
        the notification that will be shown when the tweak is applied.

        `detach_notif` - A dictionary similar to the `apply_notif` attribute.

        `show_failure` - Whether a failure notification should be shown whenever
        `notify_apply` or `notify_detach` methods are called with a parameter
        `success = False`.

        `admin_required` - Whether needed to run as an admin for the tweak
        to be applied successfully. Default is `False`.
    '''

    text: str = ''
    group: str = ''
    show_failure: bool = True
    apply_notif: dict = None
    detach_notif: dict = None
    admin_required: bool = False

    def notify_apply(self, success):
        '''
        Notifies of the success or a failure of the tweak application depending
        on the `success` parameter.
        '''

        if success and self.apply_notif:
            return self._notify(self.apply_notif['title'],
                                self.apply_notif['message'])
        elif success:
            return self._notify('Application successful',
                                "We've successfully applied that tweak.")
        elif self.show_failure:
            return self._notify('Application failed',
                                "We are sorry. We couldn't apply that tweak.")

    def notify_detach(self, success):
        '''
        Notifies of the success or a failure of the tweak detach depending
        on the `success` parameter.
        '''

        if success and self.detach_notif:
            return self._notify(self.detach_notif['title'],
                                self.detach_notif['message'])
        elif success:
            return self._notify('Detach successful',
                                "We've successfully reverted that tweak.")
        elif self.show_failure:
            self._notify('Disable failed',
                         "We are sorry. We couldn't disable that tweak.")

    @staticmethod
    def _notify(title, message):
        if not App.get_running_app():
            Logger.warning('Tweaks: Skipped notification since app not running'
                           f': title: {title}, message: {message}')
            return False
        Factory.Notification(
            title_=fstring(title), message=fstring(message)).open()
        return True

    @property
    def available(self):
        # TODO more uses than only `self.admin_required`
        ''' Return whether the tweak is available or not. '''
        return ((ctypes.windll.shell32.IsUserAnAdmin() and self.admin_required)
                or not self.admin_required)


class DummyTweak:
    ''' Used for error handling. '''
    available = False
    active = False
    switch = None
    text = 'A broken tweak, sry..'
    group = 'Broken tweaks'

    def __init__(self, *args, **kw):
        Logger.warning(f'DummyTweak: Created a DummyTweak. args: {args}, '
                       f'kw: {kw}')

    def __call__(self, *args, **kw):
        TweakBase._notify(
            '[color=f55]Dummy Tweak[/color]',
            f'This [color={theme.PRIM}]tweak[/color] was constructed as a '
            'result of an [color=f55]error[/color].')
        return False

    def apply(self):
        self()

    def detach(self):
        self()


@dataclass
class CommandTweak(TweakBase):
    ''' 
    Used for tweaks requiring passing a command into the command line.
    Json can be extended as follows.
    ```
    {
        "apply_command": "@echo applying",
        "detach_command": "@echo disabling"
    }
    ```
    
    Attributes:
        `apply_command` - The command that is passed into the cmd when
        when the `apply` method is called.

        `detach_command` - Similar to `apply_command` except it does not
        have to be specified if the tweak is one-off.

        `icon` - The icon from `segmdl2.ttf` that will be used for button
        if available.
    '''

    apply_command: str = ''
    detach_command: str = ''
    icon: str = ''

    def _apply(self, command):
        # Internal use
        Logger.info(f'CmdTweak: calling {command}')
        ret = os.system(command)
        Logger.info(f'CmdTweak: System returned {ret}')
        return ret

    def apply(self):
        ''' Apply tweak and notify. Return `os.system` call return value. '''
        ret = self._apply(self.apply_command)
        self.notify_apply(not ret)
        return ret

    def detach(self):
        ''' Detach tweak and notify. Return `os.system` call return value. '''
        ret = self._apply(self.detach_command)
        self.notify_detach(not ret)
        return ret

    def __call__(self):
        ''' Calls the `apply` method. Should be used only when the
        `detach_command` attribute is not set. '''

        return self.apply()


REG_TYPES = {
    'REG_BINARY': REG_BINARY,
    'REG_DWORD': REG_DWORD,
    'REG_DWORD_LITTLE_ENDIAN': REG_DWORD_LITTLE_ENDIAN,
    'REG_DWORD_BIG_ENDIAN': REG_DWORD_BIG_ENDIAN,
    'REG_EXPAND_SZ': REG_EXPAND_SZ,
    'REG_LINK': REG_LINK,
    'REG_MULTI_SZ': REG_MULTI_SZ,
    'REG_NONE': REG_NONE,
    'REG_QWORD': REG_QWORD,
    'REG_QWORD_LITTLE_ENDIAN': REG_QWORD_LITTLE_ENDIAN,
    'REG_RESOURCE_LIST': REG_RESOURCE_LIST,
    'REG_FULL_RESOURCE_DESCRIPTOR': REG_FULL_RESOURCE_DESCRIPTOR,
    'REG_RESOURCE_REQUIREMENTS_LIST': REG_RESOURCE_REQUIREMENTS_LIST,
    'REG_SZ': REG_SZ
}

REG_TYPES_REV = {value: key for key, value in REG_TYPES.items()}

HKEY_CONSTS = {
    'HKCR': HKEY_CLASSES_ROOT,
    'HKCU': HKEY_CURRENT_USER,
    'HKLM': HKEY_LOCAL_MACHINE,
    'HKU': HKEY_USERS,
    'HKCC': HKEY_CURRENT_CONFIG
}


@dataclass
class RegistryTweak(TweakBase):
    '''
    Used for tweaks requiring editing the registry. Json can be extended
    as follows.
    ```
    {
        apply_values: {
            "HKEY\\key\\ValueName": [value, REG_TYPE]
        },
        detach_values: {
            "HKEY\\key\\ValueName": [value, REG_TYPE]
        }
    }
    ```
    Attributes:
        `apply_values` - A dictionary which's keys are the full paths to the
        registry values to change and which's values are lists composed of
        the actual value and the REG_TYPE.

        `detach_values` - A dictionary similar to `apply_values` except it is
        used when reverting the tweak.
    '''

    apply_values: dict = field(default_factory=dict)
    detach_values: dict = field(default_factory=dict)
    admin_required: bool = False

    def _apply(self, values):
        # TODO fix detach when not specified in the json, currently applies
        #      apply_values for some reason
        # internal use
        Logger.info(f'RegTweak: Applying: {values}')

        _backup_values = {}
        for path, (value, type_) in values.items():
            hkey, key_path, value_name = self._extr_from_path(path)
            type_ = REG_TYPES.get(type_, type_)
            # TODO regex?
            # prepare current values for backup
            key = OpenKeyEx(hkey, key_path, 0, KEY_READ | ARCH_FLAG)
            _bck_value, _bck_type = QueryValueEx(key, value_name)
            # set value
            Logger.info(
                f'RegTweak: Setting {path} to {value}, type: {REG_TYPES_REV.get(type_, type_)}'
            )
            try:
                key = OpenKeyEx(hkey, key_path, 0, KEY_SET_VALUE | ARCH_FLAG)
                SetValueEx(key, value_name, 0, type_, value)
            except PermissionError:  # TODO: exception list
                Logger.error(f'RegTweak: Failed to apply. Reverting..')
                self._apply(_backup_values)
                break
            else:
                # backup values
                _backup_values[path] = (_bck_value, _bck_type)
        else:
            Logger.info('RegTweak: Applied/Reverted.')
            return True  # successful
        return False  # not successful

    def apply(self):
        ''' Applies the tweak. Return `True` if successful, else `False`. '''
        ret = self._apply(self.apply_values)
        self.notify_apply(ret)
        return ret

    def detach(self):
        ''' Reverts the tweak. Return `True` if successful, else `False`. '''
        ret = self._apply(self.detach_values)
        self.notify_detach(ret)
        return ret

    def switch(self, *args):
        ''' Apply/detach depending on the current state. '''
        if self.active:
            return self.detach()
        return self.apply()

    @property
    def active(self):
        '''
        Whether `self.apply_values` match those in the registry. Return bool.
        '''

        for path, (value, _type) in self.apply_values.items():
            hkey, key_path, value_name = self._extr_from_path(path)
            try:
                key = OpenKeyEx(hkey, key_path, 0, KEY_READ | ARCH_FLAG)
                val = QueryValueEx(key, value_name)[0]
            except Exception:  # TODO lock tweak
                Logger.error(
                    f'RegTweak: Failed to read {path} in order to see if active.'
                )
            else:
                if val != value:
                    return False
        return True

    @staticmethod
    def _extr_from_path(path):
        ''' Return `HKEY`, `key` and `value_name` strings. '''
        hkey_key, value_name = os.path.split(path)
        hkey, key = hkey_key.split('\\', 1)
        return HKEY_CONSTS[hkey], key, value_name


class PythonTweak(TweakBase):
    '''
    This class serves as a template class for constructing script tweaks.
    The `PythonTweak` class is used when constructing a custom tweak loaded
    from a module present in the `tweaks` directoy. The module has to contain
    a class `PythonTweak`. If the class is missing or an exception is raised
    when reading the module, the module will be omitted from loading.

    The class should contain `apply`, `detach` methods and `active`,
    `available`, `apply_notif`, `detach_notif` attributes or read-only
    properties.
    '''

    def apply(self):
        self.notify_apply(False)

    def detach(self):
        self.notify_detach(False)

    @property
    def active(self):
        return False

    @property
    def available(self):
        return False


TWEAKS_CLASSES = {
    'DummyTweak': DummyTweak,
    'CommandTweak': CommandTweak,
    'RegistryTweak': RegistryTweak
}

import json, yaml


class TweaksMeta(type):
    tweaks_path = ''
    tweaks = []
    proxy_ref = None

    def __init__(cls, *args, **kw):
        super().__init__(*args, **kw)

        sys.path.insert(0, os.path.abspath(cls.tweaks_path))
        cls.reload_tweaks()

    def reload_tweaks(cls):
        ''' Reload all tweaks from `self.tweaks_path`. '''

        FILETYPE_FUNCS = {
            '.json': cls._load_json,
            '.py': cls._load_py,
            '.yaml': cls._load_yaml
        }
        SKIPPED_NAMES = ['__pycache__']

        for entry in os.scandir(cls.tweaks_path):
            if entry.name in SKIPPED_NAMES:
                continue

            ret = FILETYPE_FUNCS.get(
                os.path.splitext(entry.name)[1], cls._dummy_ext)(entry)

            if ret is False:  # Error
                setattr(
                    cls, entry.name,
                    DummyTweak(requested_name=os.path.splitext(entry.name)[0]))

    def _load_yaml(cls, entry):
        with open(entry.path) as f:
            try:
                return cls._load_dict(yaml.load(f), entry.name)
            except yaml.scanner.ScannerError:
                Logger.error(f'Tweaks: Failed to read {entry.name}')
                return False

    def _load_json(cls, entry):
        with open(entry.path) as f:
            try:
                return cls._load_dict(json.load(f), entry.name)
            except json.decoder.JSONDecodeError:
                Logger.error(f'Tweaks: Failed to read {entry.name}')
                return False

    def _load_dict(cls, data, fname):
        try:
            _class_name = data['tweak_class']
        except KeyError:
            Logger.error(f'Tweaks: Key "tweak_class" not found in {fname}. '
                         'DummyTweak class will be used.')
            return False

        try:
            _class = TWEAKS_CLASSES[_class_name]
        except KeyError:
            Logger.error('Tweaks: Matching tweak class not found for '
                         f'{_class_name}. File: {fname}. DummyTweak '
                         'class will be used.')
            return False

        name = os.path.splitext(fname)[0]
        data.pop('tweak_class')

        try:
            setattr(cls, name, _class(**data))  # Create class
        except TypeError:
            Logger.error('Tweaks: Failed to initialize a tweak class from '
                         f'file {fname} with data {data}. Invalid data.')
            return False

    def _load_py(cls, entry):
        _mod_name = os.path.splitext(entry.name)[0]

        try:
            mod = __import__(_mod_name)
        except Exception as ex:
            Logger.error(f'Tweaks: {ex} occured when loading {entry.name} '
                         f'PythonTweak.\n{traceback.format_exc()}')
            return False

        try:

            class Tweak(mod.PythonTweak, PythonTweak):
                pass
        except AttributeError:
            Logger.error(f'Tweaks: No PythonTweak class found in {entry.name}')
            raise
            return False

        setattr(cls, _mod_name, Tweak())
        Logger.warning(f'Tweaks: Created a PythonTweak {_mod_name}. '
                       'This may not be safe.')
        return True

    def _dummy_ext(cls, entry):
        Logger.error(f'Tweaks: No matching load func for file {entry.name}')

    def __getattr__(cls, name):
        Logger.warning('TweaksMeta: Returned a DummyTweak')
        return DummyTweak(requested_name=name)

    def __setattr__(cls, name, value):
        if type(value) in TWEAKS_CLASSES.values():
            cls.tweaks.append(value)

        return super().__setattr__(name, value)


class Tweaks(metaclass=TweaksMeta):
    tweaks_path = os.path.abspath('tweaks')


if __name__ == '__main__':
    # valid cmd tweak
    command_test_tweak = CommandTweak(
        apply_command='@echo test_apply',
        detach_command='@echo test_detach',
        show_failure=False)
    command_test_tweak.apply()
    command_test_tweak.detach()

    # invalid cmd tweak
    command_test_tweak_invalid = CommandTweak(
        apply_command='@ech_ typo',
        detach_command='@ech_ typo',
        show_failure=False)
    command_test_tweak_invalid.apply()
    command_test_tweak_invalid.detach()

    # valid registry tweak
    reg_test_tweak = Tweaks.disable_dvr
    reg_test_tweak.apply()
    reg_test_tweak.detach()

# TODO add applied/not applied tweak property to cmd tweaks
# TODO regex reg values ??
