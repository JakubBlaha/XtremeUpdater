import os
import shutil
import platform
from kivy.app import App
from kivy.factory import Factory
from tempfile import gettempdir
from humanize import naturalsize
from winreg import *
from main import IS_ADMIN, silent_exc

APP = App.get_running_app()

if platform.architecture()[0] == '32bit':
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
        if platform.release() != '10':
            return False

        key = OpenKeyEx(HKEY_CURRENT_USER, r'System\GameConfigStore')
        GameDVR_enabled = QueryValueEx(key, 'GameDVR_enabled')[0]

        key = OpenKeyEx(HKEY_LOCAL_MACHINE,
                        r'SOFTWARE\Policies\Microsoft\Windows\GameDVR')
        try:
            AllowGameDVR = QueryValueEx(key, 'AllowGameDVR')[0]

        except OSError:
            AllowGameDVR = 1

        return GameDVR_enabled or AllowGameDVR

    @staticmethod
    @silent_exc
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
    def switch_fth(__, enabled):
        key = OpenKey(
            HKEY_LOCAL_MACHINE,
            r'SOFTWARE\Microsoft\FTH',
            access=KEY_WRITE | VIEW_FLAG)
        SetValueEx(key, 'Enabled', None, REG_DWORD, enabled)
