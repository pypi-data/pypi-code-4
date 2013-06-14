ISO2_CODES = set()

def load_modules():
    from fanery.filelib import filedir, listdir, isdir, isfile, joinpath, splitext
    for name in listdir(filedir(__file__)):
        iso2 = splitext(name)[0] if isfile(name) else (name if isdir(name) else None)
        if iso2 and len(iso2) == 2 and iso2.isupper():
            ISO2_CODES.add(iso2)

load_modules()
