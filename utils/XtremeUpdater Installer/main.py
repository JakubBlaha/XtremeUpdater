from colorama import init
init()
from termcolor import colored as c
import os
from pygit2 import clone_repository
from win32com.client import Dispatch

REPO_URL = 'https://github.com/XtremeWare/XtremeUpdater-Distribution'
usr_path = os.path.expanduser('~')

print('Welcome to', c('XtremeUpdater', 'cyan'), 'setup', c('\nPlease do not close this window until the setup is finished\n', 'yellow'))

path = usr_path + '\\AppData\\Local\\XtremeUpdater\\'
print(f'Installation path is:', c(path, 'cyan'))

print('Clonning', c('XtremeUpdater-Distribution', 'cyan'), 'repo from adress', c(REPO_URL, 'cyan'))
os.makedirs(path, exist_ok=True)
try:
    clone_repository(REPO_URL, path)
except Exception as e:
    print(c('Failed to clone the repo', 'red'), e, sep='\n')
    input(); exit()

start_path = usr_path + '\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\'
launcher_path = path + '\XtremeUpdater\launcher.exe'
lnk_path = start_path + 'XtremeUpdater.lnk'

shell = Dispatch('WScript.Shell')
shortcut = shell.CreateShortCut(lnk_path)
shortcut.Targetpath = launcher_path
shortcut.IconLocation = launcher_path
shortcut.WorkingDirectory = os.path.dirname(launcher_path)
shortcut.save()

os.startfile(lnk_path)
