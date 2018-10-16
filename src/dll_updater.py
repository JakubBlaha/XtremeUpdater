from kivy.app import App
from urllib.request import urlopen
from bs4 import BeautifulSoup
from shutil import copy, rmtree
import os

def get_data(url):
    return urlopen(url).read()

class DllUpdater:
    URL = "https://github.com/XtremeWare/XtremeUpdater/tree/master/dll/"
    RAW_URL = "https://github.com/XtremeWare/XtremeUpdater/raw/master/dll/"
    BACKUP_DIR = ".backup/"
    CACHE_DIR = '.cache/dlls/'
    available_dlls = []

    @staticmethod
    def local_dlls(path):
        for dirpath, __, filenames in os.walk(path):
            for f in filenames:
                if f.endswith('.dll'):
                    yield dirpath.replace(path, '') + f'\\{f}'

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

    @classmethod
    def _download_dll(cls, dllname):
        os.makedirs(cls.CACHE_DIR, exist_ok=True)

        _adress = cls.RAW_URL + dllname
        _data = get_data(_adress)

        with open(cls.CACHE_DIR + dllname, 'wb') as f:
            f.write(_data)

        return _data

    @classmethod
    def _backup_dll(cls, path, dll):
        dst = cls.BACKUP_DIR + os.path.splitdrive(path)[1] + dll

        os.makedirs(os.path.dirname(dst), exist_ok=True)

        copy(path + dll, dst)

    @classmethod
    def update_dlls(cls, path, dlls):
        rmtree(cls.CACHE_DIR, ignore_errors=True)

        dll_count = len(dlls)
        for index, dll in enumerate(dlls):
            dll_name = os.path.basename(dll)
            local_dll_path = path + dll

            try:
                with open(cls.CACHE_DIR + dll_name, 'rb') as f:
                    data = f.read()
            except FileNotFoundError:
                data = cls._download_dll(dll_name)
                
            with open(local_dll_path, 'rb') as f:
                local_dll_data = f.read()

            if data != local_dll_data:
                cls._backup_dll(path, dll)
                copy(cls.CACHE_DIR + dll_name, path + dll)

            App.get_running_app().root.bar.set_value(1 / dll_count * (index + 1))

        App.get_running_app().root.bar.ping()

    def restore_dlls(self, path: str, dlls: list) -> tuple:
        '''Returns ([restored], [not restored])'''

        restored = []
        for dll in dlls:
            src = os.path.abspath(self.BACKUP_DIR + os.path.splitdrive(path)[1] + dll)
            dst = os.path.abspath(path + dll)
            try:
                copy(src, dst)
            except FileNotFoundError:
                pass
            else:
                os.remove(src)
                restored.append(dll)
        
        return (restored, set(dlls) - set(restored))

    def available_restore(self, path):
        bck_path = os.path.abspath(os.path.join(self.BACKUP_DIR, path))

        return os.listdir(bck_path)
