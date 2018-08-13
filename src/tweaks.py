import shutil
import os
from tempfile import gettempdir
from hurry.filesize import size
from kivy.app import App
from winreg import *


APP = App.get_running_app()

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
        final_size_str = size(init_size - finish_size)
        final_size_str += '' if final_size_str.endswith('B') else 'B'

        APP.root.bar.ping()

    @staticmethod
    def is_dvr():
        reg = ConnectRegistry(None, HKEY_CURRENT_USER)
        key = OpenKey(reg, r'System\GameConfigStore')
        GameDVR_enabled = QueryValueEx(key, 'GameDVR_enabled')[0]

        reg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
        key = OpenKey(reg, r'SOFTWARE\Policies\Microsoft\Windows')
        try:
            key = CreateKey(key, 'GameDVR')
            AllowGameDVR = QueryValueEx(key, 'AllowGameDVR')[0]

        except:
            AllowGameDVR = 1

        return GameDVR_enabled or AllowGameDVR

    def switch_dvr(_, enabled):
        reg = ConnectRegistry(None, HKEY_CURRENT_USER)
        key = OpenKey(reg, r'System\GameConfigStore', 0, KEY_SET_VALUE)
        SetValueEx(key, 'GameDVR_enabled', None, REG_DWORD, enabled)

        reg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
        key = OpenKey(reg, r'SOFTWARE\Policies\Microsoft\Windows\GameDVR', 0, KEY_SET_VALUE)
        SetValueEx(key, 'AllowGameDVR', None, REG_DWORD, enabled)

        APP.root.bar.ping()
