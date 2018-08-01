import os
from pygit2 import Repository, GIT_RESET_HARD
from traceback import format_exc

UP_TO_DATE = 'Already up to date.'

repo = Repository(os.getcwd() + '\\repo')
try:
    repo.remotes['origin'].fetch()
    repo.reset(repo.lookup_reference('refs/remotes/origin/master').get_object().oid, GIT_RESET_HARD)
except:
    print(format_exc())

try:
    os.startfile(os.path.abspath('repo/XtremeUpdater/Xtreme.exe'))
except OSError:
    print(format_exc())
    