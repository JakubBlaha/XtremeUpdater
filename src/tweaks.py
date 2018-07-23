import shutil
import os
from tempfile import gettempdir
from hurry.filesize import size
from kivy.app import App


def get_size(path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            path = os.path.join(dirpath, f)
            total_size += os.path.getsize(path)
    
    return total_size


class Tweaks:
    @staticmethod
    def clear_temps():
        tmp_dir = gettempdir()
        init_size = get_size(tmp_dir)

        shutil.rmtree(tmp_dir, ignore_errors=True)

        finish_size = get_size(tmp_dir)
        final_size_str = size(init_size - finish_size)
        final_size_str += '' if final_size_str.endswith('B') else 'B'

        App.get_running_app().root.info(f'Deleted temp directory | Freed up {final_size_str}')
