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
    available_dlls = []

    @staticmethod
    def local_dlls(path):
        return [
            item for item in os.listdir(path)
            if os.path.splitext(item)[1] == '.dll'
        ]

    def load_available_dlls(self):
        try:
            html = get_data(self.URL)
            soup = BeautifulSoup(html, 'html.parser')
            for a in soup.find_all('a', {'class': 'js-navigation-open'}):
                if a.parent.parent.get('class')[0] == 'content':
                    self.available_dlls.append(a.text)

        except:
            return False

        else:
            return True                       

    def _download_dll(self, dllname):
        _adress = os.path.join(self.RAW_URL, dllname)
        _data = get_data(_adress)

        return _data

    def _backup_dll(self, path, dll):
        dst = os.path.realpath(
            os.path.join(self.BACKUP_DIR,
                         os.path.splitdrive(path)[1][1:]))

        if not os.path.exists(dst):
            os.makedirs(dst)

        copy(os.path.join(path, dll), dst)

    @staticmethod
    def _overwrite_dll(path, data):
        with open(path, 'wb') as f:
            f.write(data)

    def update_dlls(self, path, dlls):
        dll_num = len(dlls)

        for index, dll in enumerate(dlls):
            info(
                f"Downloading {dll} ({index + 1} of {dll_num}) | Please wait.."
            )
            data = self._download_dll(dll)

            local_dll_path = os.path.join(path, dll)
            with open(local_dll_path, 'rb') as f:
                local_dll_data = f.read()

            if data == local_dll_data:
                continue

            self._backup_dll(path, dll)
            self._overwrite_dll(local_dll_path, data)

    def restore_dlls(self, path, dlls):
        dll_num = len(dlls)
        bck_path = os.path.abspath(
            os.path.join(self.BACKUP_DIR,
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

    def available_restore(self, path):
        bck_path = os.path.abspath(os.path.join(self.BACKUP_DIR, path))

        return os.listdir(bck_path)

    @staticmethod
    def dll_subdirs(path, available_dlls):
        dll_dirs = []
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                if f.endswith('.dll') and f in available_dlls:
                    dll_dirs.append(dirpath.replace(path, ''))
                    break

        return dll_dirs[1:]