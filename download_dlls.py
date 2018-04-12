import urllib.request
import os

import extractdllnames

domain = r"https://mobasuite.com/downloads/dlls/"
directory = "dll/"

if not os.path.exists(directory):
    os.makedirs(directory)

print("Gathering dll names..")
dlls_to_download = extractdllnames.get_dll_names()

for dll in dlls_to_download:
    path = domain + dll
    print("Downloading:", dll, path, flush=True)

    data = urllib.request.urlopen(path).read()
    with open(directory + dll, 'wb') as file:
        file.write(data)
