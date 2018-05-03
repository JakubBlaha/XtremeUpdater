import os
import sys

from PIL import Image, ImageTk


# https://stackoverflow.com/a/44352931
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def get_img(relative_path, _type="tk"):
    path = resource_path(relative_path)

    img = Image.open(path)
    if _type is "tk":
        container.cont.append(tkimage(img))
    elif _type is "PIL":
        container.cont.append(img)

    return container.cont[-1]

def tkimage(img):
    tk_img = ImageTk.PhotoImage(img)
    container.cont.append(tk_img)
    
    return container.cont[-1]

class container:
    cont = []