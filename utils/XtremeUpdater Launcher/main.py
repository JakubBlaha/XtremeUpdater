import os
from pygit2 import Repository, GIT_RESET_HARD

UP_TO_DATE = 'Already up to date.'

print('Fetching repo..')
try:
    repo = Repository(os.path.dirname(os.getcwd()))
    repo.reset(repo.lookup_reference('refs/remotes/origin/master').get_object().oid, GIT_RESET_HARD)
except Exception as e:
    print('Failed to fetch!', e, sep='\n')
else:
    print('Successfully fetched repo')

print('Starting XtremeUpdater')
os.startfile('XtremeUpdater.exe')
    