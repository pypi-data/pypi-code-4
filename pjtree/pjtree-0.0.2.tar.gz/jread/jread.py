# -*- utf-8 -*-


def set_argument(parser):
    u""" Set argument.

    @param parser ArgumentParser
    """
    parser.add_argument('-f', '--file', help='Json file')
    parser.add_argument('path', type=str, default=None)
    parser.add_argument('--encoding', type=str, default='utf-8')


def scan(data, path, enc):
    u""" Scan directory and files.

    If scan file is direcotry, Add dict.
    Otherwise Add string.

    @param data dict data.
    @param path file path.

    @return dict data.
    """
    import os
    import base64

    files = os.listdir(path)
    for f in files:
        f_path = os.path.join(path, f)
        if os.path.isdir(f_path):
            data[f] = scan({}, f_path, enc)
        else:
            fi = open(f_path, 'rb')
            body = base64.b64encode(fi.read())
            data[f] = 'b64:' + body.decode(enc)
            fi.close()
    return data


def show(data):
    u""" Show json in data.

    Dict data dump to stdo`ut.
    @param data dict data.
    """
    import json

    print(json.dumps(data, sort_keys=True, indent=4, ensure_ascii=False))


def save(data, path, enc):
    u""" Save json file in data.

    Dict data dump to json file.
    @param data dict data
    @param path json path
    @param enc  json endoing
    """
    import json
    import codecs

    fo = codecs.open(path, 'w', enc)
    json.dump(data, fo, sort_keys=True, indent=4, ensure_ascii=False)
    fo.close()
