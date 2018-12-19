import pygit2
import os, sys
import urllib.request
import tempfile
import subprocess
from kivy.logger import Logger

class UpdateClient:
    UTIL_URL = 'https://github.com/XtremeWare/XtremeUpdater/raw/master/utils/Updater/updater-utility/update-utility.exe'
    
    _util_path = ''
    _repo_path = ''

    def __init__(self, repo_path):
        self._repo_path = repo_path
        
        try:
            self.repo = pygit2.Repository(repo_path)
        except pygit2.GitError:
            Logger.error(f'UpdateClient: Failed to load repo at {repo_path}!')
        else:
            Logger.info(f'UpdateClient: Located repo at {repo_path}')
        
        TMP_DIR = tempfile.gettempdir()
        self._util_path = os.path.join(TMP_DIR, 'XtremeUpdater/update-utility/utility.exe')

    def is_update_available(self):
        try:
            self.repo.remotes['origin'].fetch()
        except Exception:
            Logger.error('UpdateClient: Failed to fetch origin!')
            return None
        else:
            Logger.info('UpdateClient: Fetched origin')

        status = self.repo.status()
        Logger.info(f'UpdateClient: Original status: {status}')

        # Filter out ignored files
        considered_status = {}
        for key, flag in status.items():
            if flag == pygit2.GIT_STATUS_IGNORED:
                Logger.warning(f'UpdateClient: Ignored key `{key}`')
                continue
            considered_status[key] = flag

        Logger.info(f'UpdateClient: Considered status: {considered_status}')
        return considered_status

    def download_util(self, hook=None):
        os.makedirs(os.path.split(self._util_path)[0], exist_ok=True)
        try:
            urllib.request.urlretrieve(self.UTIL_URL, self._util_path, reporthook=hook)
        except Exception:
            Logger.error(f'UpdateClient: Failed to retrieve {self.UTIL_URL} to {self._util_path}')
            return False
        
        Logger.info(f'UpdateClient: Retrieved {self.UTIL_URL} to {self._util_path}')
        return True

    def run_util(self):
        try:
            subprocess.Popen([self._util_path, self._repo_path])
        except Exception:
            Logger.error(f'UpdateClient: Failed to execute {self._util_path} with an argument {self._repo_path}')
            return False

        Logger.info(f'UpdateClient: Executed {self._util_path} with an argument {self._repo_path}')
        return True


if __name__ == '__main__':
    c = UpdateClient(r"C:\Users\jakub\AppData\Local\XtremeUpdater\repo")
    print(c.is_update_available())
    c.download_util()
    c.run_util()