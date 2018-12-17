import pygit2
import os, sys
import urllib.request
import tempfile
import subprocess

class UpdateClient:
    UTIL_URL = 'https://github.com/XtremeWare/XtremeUpdater/raw/master/utils/Updater/updater-utility/update-utility.exe'
    
    _util_path = ''
    _repo_path = ''

    def __init__(self, repo_path):
        self._repo_path = repo_path
        self.repo = pygit2.Repository(repo_path)
        
        TMP_DIR = tempfile.gettempdir()
        self._util_path = os.path.join(TMP_DIR, 'XtremeUpdater/update-utility/utility.exe')

    def is_update_available(self):
        try:
            self.repo.remotes['origin'].fetch()
        except Exception:
            return None

        return self.repo.status()

    def download_util(self, hook=None):
        os.makedirs(os.path.split(self._util_path)[0], exist_ok=True)
        try:
            urllib.request.urlretrieve(self.UTIL_URL, self._util_path, reporthook=hook)
        except Exception:
            return False

        return True

    def run_util(self):
        try:
            subprocess.Popen([self._util_path, self._repo_path])
        except Exception:
            return False

        return True

if __name__ == '__main__':
    c = UpdateClient(r"C:\Users\jakub\AppData\Local\XtremeUpdater\repo")
    print(c.is_update_available())
    c.download_util()
    c.run_util()