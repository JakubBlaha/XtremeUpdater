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
            self.error(f'Failed to load repo at {repo_path}!')
        else:
            self.info(f'Located repo at {repo_path}')
        
        TMP_DIR = tempfile.gettempdir()
        self._util_path = os.path.join(TMP_DIR, 'XtremeUpdater/update-utility/utility.exe')

    def is_update_available(self):
        try:
            self.repo.remotes['origin'].fetch()
        except Exception:
            self.error('Failed to fetch origin!')
            return None
        else:
            self.info('Fetched origin')

        IGNORED_PHRASES = ('.cache', '.config', '.backup', 'logs') # HOTFIX
        status = self.repo.status()
        self.info(f'Original status: {status}')
        for key in tuple(status.keys()):
            for phrase in IGNORED_PHRASES:
                if phrase in key:
                    self.warning(f'Ignored key |{key}| with value |{status.pop(key)}| in conflict with |{phrase}|')
                    break

        self.info(f'Considered status: {status}')
        return status

    def download_util(self, hook=None):
        os.makedirs(os.path.split(self._util_path)[0], exist_ok=True)
        try:
            urllib.request.urlretrieve(self.UTIL_URL, self._util_path, reporthook=hook)
        except Exception:
            self.error(f'Failed to retrieve {self.UTIL_URL} to {self._util_path}')
            return False
        
        self.info(f'Retrieved {self.UTIL_URL} to {self._util_path}')
        return True

    def run_util(self):
        try:
            subprocess.Popen([self._util_path, self._repo_path])
        except Exception:
            self.error(f'Failed to execute {self._util_path} with an argument {self._repo_path}')
            return False

        self.info(f'Executed {self._util_path} with an argument {self._repo_path}')
        return True

    def info(self, info):
        return Logger.info('UpdateClient: ' + info)

    def error(self, error):
        return Logger.error('UpdateClient: ' + error)

    def warning(self, warning):
        return Logger.warning('UpdateClient: ' + warning)

if __name__ == '__main__':
    c = UpdateClient(r"C:\Users\jakub\AppData\Local\XtremeUpdater\repo")
    print(c.is_update_available())
    c.download_util()
    c.run_util()