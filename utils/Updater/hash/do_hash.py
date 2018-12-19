import os
from hashlib import sha1

EXE_PATH = os.path.abspath(r'..\update-utility\update-utility.exe')
HASH_FILE_FILENAME = 'sha1'

hash_default = input(f'Hash file {EXE_PATH}? [y]/n: ') != 'n'
if not hash_default:
    EXE_PATH = os.path.abspath(input('Path to hashed file: '))

with open(EXE_PATH, 'rb') as f:
    bytes_ = f.read()

hash_ = sha1(bytes_).hexdigest()

write_file = input(f'Write hash {hash_} to file {HASH_FILE_FILENAME}? [y]/n: ') != 'n'
if write_file:
    with open(HASH_FILE_FILENAME, 'w') as f:
        f.write(hash_)
