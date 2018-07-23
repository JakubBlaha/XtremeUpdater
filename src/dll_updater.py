from kivy.app import App
from urllib.request import urlopen
from bs4 import BeautifulSoup
from shutil import copy
import os

info = lambda text: App.get_running_app().root.info(text)
get_data = lambda url: urlopen(url).read()

class DllUpdater:
    URL = "https://github.com/XtremeWare/XtremeUpdater/tree/master/dll/"
    RAW_URL = "https://github.com/XtremeWare/XtremeUpdater/raw/master/dll/"
    BACKUP_DIR = ".backup/"

    @staticmethod
    def local_dlls(path):
        return [
            item for item in os.listdir(path)
            if os.path.splitext(item)[1] == '.dll'
        ]

    @classmethod
    def available_dlls(cls):
        html = get_data(cls.URL)

        available_dlls = []
        soup = BeautifulSoup(html, 'html.parser')
        for a in soup.find_all('a', {'class': 'js-navigation-open'}):
            if a.parent.parent.get('class')[0] == 'content':
                available_dlls.append(a.text)

        return available_dlls

    @classmethod
    def _download_dll(cls, dllname):
        _adress = os.path.join(cls.RAW_URL, dllname)
        _data = get_data(_adress)

        return _data

    @classmethod
    def _backup_dll(cls, path, dll):
        dst = os.path.realpath(
            os.path.join(cls.BACKUP_DIR,
                         os.path.splitdrive(path)[1][1:]))

        if not os.path.exists(dst):
            os.makedirs(dst)

        copy(os.path.join(path, dll), dst)

    @staticmethod
    def _overwrite_dll(path, data):
        with open(path, 'wb') as f:
            f.write(data)

    @classmethod
    def update_dlls(cls, path, dlls):
        dll_num = len(dlls)

        for index, dll in enumerate(dlls):
            info(
                f"Downloading {dll} ({index + 1} of {dll_num}) | Please wait.."
            )
            data = cls._download_dll(dll)

            local_dll_path = os.path.join(path, dll)
            with open(local_dll_path, 'rb') as f:
                local_dll_data = f.read()

            if data == local_dll_data:
                continue

            cls._backup_dll(path, dll)
            cls._overwrite_dll(local_dll_path, data)

    @classmethod
    def restore_dlls(cls, path, dlls):
        dll_num = len(dlls)
        bck_path = os.path.abspath(
            os.path.join(cls.BACKUP_DIR,
                         os.path.splitdrive(path)[1][1:]))

        restored = 0
        for index, dll in enumerate(dlls):
            i = index + 1

            backed_dll_path = os.path.join(bck_path, dll)
            try:
                copy(backed_dll_path, path)
            except:
                pass
            else:
                restored += 1

        info(f"Done | Restored {restored} of {dll_num} dlls")

    @classmethod
    def available_restore(cls, path):
        bck_path = os.path.abspath(os.path.join(cls.BACKUP_DIR, path))

        return os.listdir(bck_path)