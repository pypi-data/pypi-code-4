from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)
from .home import Home


def main():
    home = Home()
    home = input('Thanks for using SIGACTor. Press any key to exit.')
    print(home)

if __name__ == "__main__":
    main()
