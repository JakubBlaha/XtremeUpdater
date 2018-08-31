import os
from pygit2 import Repository, GIT_RESET_HARD
from traceback import format_exc

UP_TO_DATE = 'Already up to date.'

repo = Repository(os.getcwd() + '\\repo')
repo.remotes['origin'].fetch()
repo.reset(repo.lookup_reference('refs/remotes/origin/master').get_object().oid, GIT_RESET_HARD)

os.chdir('repo/XtremeUpdater')
os.startfile(os.path.abspath('Xtreme.exe'))
    
