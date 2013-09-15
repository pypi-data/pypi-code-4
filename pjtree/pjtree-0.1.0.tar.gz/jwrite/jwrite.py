# -*- utf-8 -*-


def set_argument(parser):
    u""" Set argument.

    @param parser ArgumentParser
    """
    parser.add_argument('-f', '--file', help='Json file')
    parser.add_argument('json', type=str, default=None)
    parser.add_argument('path', type=str, default=None)
    parser.add_argument('--encoding',  type=str, default='utf-8')
    parser.add_argument('--force', help="Force overwrite all files.", action="store_true", default=False)
    parser.add_argument('--notoverwrite', help="Not overwrite all files.", action="store_true", default=False)


def load_json(path, encode):
    u""" Loading json.

    Loading json file.

    @param path   json file path.
    @param encode file encode.

    @return dict
    """
    import json
    import codecs
    import os

    if os.access(path, os.R_OK):
        try:
            with codecs.open(path, 'r', encode) as fi:
                data = json.load(fi)
        except ValueError:
            raise ValueError
    else:
        print('%s permission denied!' % path)

    return data


def trace(data, path, owrite=False, nowrite=False):
    u""" Trace directory or files.

    If data type is Dict, create directory.
    Otherwise, create empty file.

    @param data    dict or str
    @param path    file path
    @param owrite  overwrite flag
    @param nowrite not overwrite flag
    """
    import os

    if isinstance(data, dict):
        make_file(path,  None, owrite, nowrite)
        for k, v in data.items():
            trace(v, os.path.join(path, k), owrite, nowrite)
    else:
        make_file(path,  data, owrite, nowrite)


def make_file(path, url, owrite, nowrite=False):
    u""" Making directory or file.

    Making directory or file.
    path is making file path.
    data is download file url.

    @param path    str
    @param url     str
    @param owrite  overwrite flag
    @param nowrite not overwrite flag
    """
    import os
    import re
    def file_write(path, url, option):
        print('make %s.' % path)
        with open(path, option) as f:
            f.write(url)
        print('done.')
            

    if os.path.exists(path) and not owrite:
        if not url is None and not nowrite:
            print('already exists %s.' % path)
            ans = raw_input('overwrite?(y/n):').lower()
            if ans == 'y' or ans == 'yes':
                make_file(path, url, True)
    elif url is None:
        if not owrite:
            print('make %s' % path)
            os.mkdir(path)
            print('done.')
    elif re.match('url:', url):
        import urllib
        print('make %s' % path)
        url = url.replace('url:', '')
        urllib.urlretrieve(url, path)
        print('done.')
    elif re.match('b64:', url):
        import base64
        url = url.replace('b64:', '')
        url = base64.b64decode(url)
        file_write(path, url, 'wb')
    else:
        file_write(path, url, 'w')
