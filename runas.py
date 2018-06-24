import os

def run_as_admin(path):
    os.system(f'powershell Start-Process "{path}" -Verb RunAs')
