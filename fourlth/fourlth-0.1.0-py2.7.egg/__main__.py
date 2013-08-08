import logging

#logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('fourlth')

import sys
import os

from __init__ import *
from loader import *


def main():
    """\
Simple, interactive interpreter for testing ONLY.
"""
    
    interp = loader(sys.stdin, prompt_str='> ', interp=None)
    if interp: 
        print interp() or ''


if __name__ == '__main__':
    main()
