import os
from examples import pull
from pygit2 import Repository

UP_TO_DATE = 'Already up to date.'

print('Fetching repo..')
try:
    repo = Repository(os.path.dirname(os.getcwd()))
    pull(repo)
except:
    print('Failed to fetch!')
else:
    print('Successfully fetched repo')

print('Starting XtremeUpdater')
os.startfile('XtremeUpdater.exe')
    