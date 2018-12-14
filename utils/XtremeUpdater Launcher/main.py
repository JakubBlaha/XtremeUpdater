import os
from pygit2 import Repository, GIT_RESET_HARD, GitError
from traceback import format_exc
from _thread import start_new
import tkinter as tk
import tkinter.ttk as ttk


UP_TO_DATE = 'Already up to date.'


class Launcher(tk.Tk):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        self.title('Launching XtremeUpdater')
        self.geometry('300x70')
        self.config(padx=20, pady=20)
        self.resizable(False, False)

        self.info_lb = ttk.Label(text='Initializing..')
        self.progressbar = ttk.Progressbar(mode='indeterminate', maximum=60)
        self.progressbar.start()

        self.info_lb.pack(fill='both')
        self.progressbar.pack(fill='x')

        start_new(self.launch, ())

    def launch(self):
        # init repo
        self._info('Locating the repository..')
        try:
            repo = Repository(os.getcwd() + '\\repo')
        except GitError:
            self._error('Failed to locate the repository!')
            return
        
        # fetch
        self._info('Fetching repository..')
        try:
            repo.remotes['origin'].fetch()
        except GitError:
            self._error('Failed to fetch the repository!')

        # reset repository
        self._info('Resetting the repository..')
        try:
            repo.reset(repo.lookup_reference('refs/remotes/origin/master').get_object().oid, GIT_RESET_HARD)
        except GitError:
            self._error('Failed to reset the repository!')

        self._info('Launching..')
        try:
            os.chdir('repo/XtremeUpdater')
        except OSError:
            self._error('Failed to change directory!')
            return
        
        try:
            os.startfile(os.path.abspath('Xtreme.exe'))
        except OSError:
            self._error('Failed to launch!')
        else:
            self.destroy()


    def _info(self, text):
        self.info_lb.config(text=text, foreground='black')

    def _error(self, text):
        self.info_lb.config(text=text, foreground='red')
        self.progressbar.stop()
        self.progressbar.config(mode='determinate')


if __name__ == '__main__':
    Launcher().mainloop()
