from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
import json

TEMPLATE = 'https://www.google.com/search?q={}&source=lnms&tbm=isch'
HEADERS = {
        'User-Agent':
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"
}

def get_image_url(query, index=0):
    query = query.split()
    query = '+'.join(query)
    url = TEMPLATE.format(query)
    req = Request(url, headers=HEADERS)
    html = urlopen(req)
    
    return get_image_url_from_response(html, index)

def get_image_url_from_response(response, index=0):
    soup = BeautifulSoup(response, 'html.parser')

    div = soup.find_all('div', {'class': 'rg_meta'})[index]
    link = json.loads(div.text)["ou"]

    return link
