#! /usr/bin/env python

from xdress.autoall import pycparser_findall

def main():
    print pycparser_findall( 
        'glext.h',
        includes=('/usr/include',),
        verbose=True,
        debug=True,
    )
if __name__ == "__main__":
    main()
