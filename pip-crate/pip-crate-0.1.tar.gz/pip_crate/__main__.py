import sys
from . import main

if __name__ == '__main__':
    exit = main()
    if exit:
        sys.exit(exit)
