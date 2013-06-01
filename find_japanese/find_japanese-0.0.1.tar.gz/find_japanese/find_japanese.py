def find_japanese(path, only_path_name=False):
    import os

    if not os.path.exists(path):
        return

    if os.path.isfile(path):
        _find_japanese(path, only_path_name)
    else:
        for fpath, _, names in os.walk(path):
            for name in names:
                _find_japanese(os.path.join(fpath, name), only_path_name)

def _find_japanese(file_path, only_path_name):
    import re
    r = re.compile("[ぁ-んァ-ンー\u4e00-\u9FFF]+")
    with open(file_path) as f:
        for index, line in enumerate(f):
            if r.search(line) is not None:
                if only_path_name:
                    print("{path}".format(path=file_path)) 
                    break
                else:
                    print("{n}: {path}\n {line}".format(n=index, line=line, path=file_path))
