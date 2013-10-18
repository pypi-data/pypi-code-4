#!/usr/bin/env python
import doc


def main(argv):
    d = doc.Doc(argv[1])
    for a in argv[2:]:
        print make_line(d, a)

def make_enviroment_name(name):
    return name.upper().replace(".","_")

def make_line(doc, name):
    temp = doc
    for attr in name.split("."):
        temp = getattr(temp, attr)
    if type(temp) != str:
        temp = str(temp)
    temp = temp.replace(" ", "_")
    return "export %s=%s" % ( make_enviroment_name(name) , temp)
        
# `./read_config.py  gui.xml guidata.skin.scoreFontName guidata.skin.scoreFontHeight`

if __name__ == '__main__':
    import sys
    main(sys.argv)
