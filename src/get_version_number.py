from win32api import GetFileVersionInfo, LOWORD, HIWORD


def get_version_number(filename):
    try:
        info = GetFileVersionInfo(filename, "\\")
        ms = info['FileVersionMS']
        ls = info['FileVersionLS']
        return '.'.join(
            map(str, (HIWORD(ms), LOWORD(ms), HIWORD(ls), LOWORD(ls))))

    except:
        return f'N/A'
