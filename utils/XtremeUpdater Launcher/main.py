import git, os

UP_TO_DATE = 'Already up to date.'

g = git.Git()
print('Fetching repo..')
try:
    result = g.pull('origin', 'master')
except:
    print('Failed to fetch!')
else:
    print('Successfully fetched repo')

print('Starting XtremeUpdater')
os.system('XtremeUpdater.exe')
    