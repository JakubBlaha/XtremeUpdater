import shutil
import os
from tempfile import gettempdir
from hurry.filesize import size
from main import info

def get_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    
    return total_size

class Tweaks:
    @staticmethod
    def clear_temps():
        _init_size = get_size(gettempdir())

        shutil.rmtree(gettempdir(), ignore_errors=True)

        _finish_size = get_size(gettempdir())
        _final_size_str = size(_init_size - _finish_size).replace('B', '') + 'B'

        info(f'Deleted temp directory | Freed up {_final_size_str}')
