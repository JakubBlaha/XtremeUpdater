import os
from pygit2 import Repository, GIT_RESET_HARD

UP_TO_DATE = 'Already up to date.'

repo = Repository(os.path.dirname(os.getcwd()))
try:
    repo.reset(repo.lookup_reference('refs/remotes/origin/master').get_object().oid, GIT_RESET_HARD)
except:
    pass

try:
    os.startfile('XtremeUpdater.exe')
except OSError:
    pass
    