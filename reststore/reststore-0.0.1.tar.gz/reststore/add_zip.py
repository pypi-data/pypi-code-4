from __future__ import print_function
import sys
import zipfile


def add(files, filepath, password=None):
    """Add files from the zip file at filepath"""
    if not zipfile.is_zipfile(filepath):
        raise TypeError("Not a zipfile %s" % filepath)

    zf = zipfile.ZipFile(filepath)
    if password is not None:
        zf.setpassword(password)
    for i, name in enumerate(zf.namelist()):
        data = zf.read(name, pwd=password)
        hexdigest = files.bulk_put(data)
        print("put %s" % hexdigest, file=sys.stderr)
        if i % 100 == 0:
            print("flush ...", file=sys.stderr)
            files.bulk_flush()
    print("flush ...", file=sys.stderr)
    files.bulk_flush()

