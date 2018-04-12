from os.path import splitext
import urllib.request

def get_dll_names():
    text = urllib.request.urlopen("https://mobasuite.com/downloads/dlls").read().decode()

    reading_string = False
    strs = []
    string = ""

    for char in text:
        if char == '"' and not reading_string:
            reading_string = True
        elif char == '"' and reading_string:
            reading_string = False
            strs.append(string)
            string = ""
        elif reading_string:
            string += char

    dlls = tuple(s for s in strs if splitext(s)[1] == ".dll")

    return dlls

def __main():
    input(tuple(s.lower() for s in get_dll_names()))

if __name__ == '__main__':
    __main()