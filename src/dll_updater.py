from kivy.app import App
from urllib.request import urlopen
from shutil import copy, rmtree
from github import Github
import os


def get_data(url):
    return urlopen(url).read()


def ensure_git(fn):
    def wrapper(self, *args, **kw):
        if not getattr(self, 'git'):
            self.git = Github()
        return fn(self, *args, **kw)

    return wrapper

def ensure_repo(fn):
    def wrapper(self, *args, **kw):
        if not getattr(self, 'repo'):
            self.repo = self.git.get_repo(DllUpdater.REPO_NAME)
        return fn(self, *args, **kw)

    return wrapper


class DllUpdater:
    URL = "https://github.com/XtremeWare/XtremeUpdater/tree/master/dll/"
    RAW_URL = "https://github.com/XtremeWare/XtremeUpdater/raw/master/dll/"
    BACKUP_DIR = ".backup/"
    CACHE_DIR = '.cache/dlls/'
    REPO_NAME = 'JakubBlaha/XtremeUpdater'
    available_dlls = ()

    git = None
    repo = None

    @staticmethod
    def local_dlls(path):
        for dp, __, fs in os.walk(path):
            for f in fs:
                if f.endswith(".dll"):
                    yield dp.replace(path, '') + f'\\{f}'

    @ensure_git
    @ensure_repo
    def load_available_dlls(self):
        try:
            contents = self.repo.get_dir_contents('dll')
        except Exception:
            return False
        else:
            self.available_dlls = [i.name for i in contents]
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

            App.get_running_app().root.bar.set_value(
                1 / dll_count * (index + 1))

        App.get_running_app().root.bar.ping()

    def restore_dlls(self, path: str, dlls: list) -> tuple:
        '''Returns ([restored], [not restored])'''

        restored = []
        for dll in dlls:
            src = os.path.abspath(self.BACKUP_DIR +
                                  os.path.splitdrive(path)[1] + dll)
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
