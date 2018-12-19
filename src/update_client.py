import pygit2
import os, sys
import urllib.request
import tempfile
import subprocess
from kivy.logger import Logger
from hashlib import sha1


class UpdateClient:
    UTIL_URL = 'https://github.com/XtremeWare/XtremeUpdater/raw/master/utils/Updater/updater-utility/update-utility.exe'
    HASH_URL = 'https://raw.githubusercontent.com/XtremeWare/XtremeUpdater/master/utils/Updater/hash/sha1'

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
        self._util_path = os.path.join(
            TMP_DIR, 'XtremeUpdater/update-utility/utility.exe')

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
            urllib.request.urlretrieve(
                self.UTIL_URL, self._util_path, reporthook=hook)
        except Exception:
            Logger.error(
                f'UpdateClient: Failed to retrieve {self.UTIL_URL} to {self._util_path}'
            )
            return False

        Logger.info(
            f'UpdateClient: Retrieved {self.UTIL_URL} to {self._util_path}')
        return True

    def run_util(self):
        try:
            subprocess.Popen([self._util_path, self._repo_path])
        except Exception:
            Logger.error(
                f'UpdateClient: Failed to execute {self._util_path} with an argument {self._repo_path}'
            )
            return False

        Logger.info(
            f'UpdateClient: Executed {self._util_path} with an argument {self._repo_path}'
        )
        return True

    def is_newest_util(self):
        ''' Compares hashes of local and remote versions of the update-utility. '''

        if not os.path.isfile(self._util_path):
            Logger.warning(
                f'UpdateClient: Could not find a local copy of the update-utility in {self._util_path}'
            )
            return False
        Logger.info(
            f'UpdateClient: Found a local copy of the update-utility in {self._util_path}'
        )

        try:
            newest_hash = urllib.request.urlopen(
                self.HASH_URL).read().decode('utf-8')
        except Exception:
            Logger.error(
                f'UpdateClient: Failed to retrieve update-utility hash from {self.HASH_URL}'
            )
            return False
        Logger.info(
            f'UpdateClient: Remote update-utility hash from {self.HASH_URL} is {newest_hash}'
        )

        try:
            with open(self._util_path, 'rb') as f:
                bytes_ = f.read()
        except OSError:
            Logger.error('UpdateClient: Failed to hash the local copy')
            return False

        hash_ = sha1(bytes_).hexdigest()
        Logger.info(f'UpdateClient: Hash of the local copy is {hash_}')
        return newest_hash == hash_
