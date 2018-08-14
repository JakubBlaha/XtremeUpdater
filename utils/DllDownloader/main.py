import os
from urllib.request import urlopen
from bs4 import BeautifulSoup
from pathlib import Path

URL = 'https://mobasuite.com/_p/'
TARGET = str(Path(__file__).parents[2]) + '/dll'
LAST = 'last.html'

print('Source:', URL)
print('Target:', TARGET)
print('')

html = urlopen(URL).read()
soup = BeautifulSoup(html, 'html.parser')

if os.path.exists(LAST):
    with open(LAST, 'rb') as last:
        last_html = last.read()
    
    if html == last_html:
        input('Update not required')
        exit()

hrefs = []
for a in soup.find_all('a'):
    hrefs.append(a.get('href'))

dlls = [i for i in hrefs if os.path.splitext(i)[1] == '.dll']
download_urls = [os.path.join(URL, dll) for dll in dlls]

for dll, url in zip(dlls, download_urls):
    print('Downloading:', url)
    with open(os.path.join(TARGET, dll).lower(), 'wb') as stream:
        stream.write(urlopen(url).read())

with open(LAST, 'wb') as last:
    last.write(html)

print('Written last')

input('\nFinished')