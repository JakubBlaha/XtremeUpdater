from kivy.app import App
from kivy.logger import Logger
from tempfile import gettempdir
import os

BATCH_DATA = \
'''
@echo We are about to uninstall XtremeUpdater. Thanks for installing!
@timeout /t 10 /nobreak\n
@rmdir /q /s %localappdata%\\XtremeUpdater
'''
BATCH_PATH = os.path.join(gettempdir(),
                          r'XtremeUpdater\uninstall\uninstall.bat')
LNK_PATH = os.path.expanduser(
    '~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\XtremeUpdater.lnk'
)

def uninstall():
    ''' Deletes Start Menu shortcut and the repo. '''

    try:
        os.remove(LNK_PATH)
    except FileNotFoundError:
        Logger.error(f'Uninstaller: Failed to remove lnk at {LNK_PATH}')
    else:
        Logger.info(f'Uninstaller: Removed lnk at {LNK_PATH}')

    os.makedirs(os.path.dirname(BATCH_PATH), exist_ok=True)
    Logger.info('Uninstaller: Writing the batch file..')
    with open(BATCH_PATH, 'w') as f:
        f.write(BATCH_DATA)

    Logger.info('Uninstaller: Running the batch file..')
    os.startfile(BATCH_PATH)
    App.get_running_app().stop()
