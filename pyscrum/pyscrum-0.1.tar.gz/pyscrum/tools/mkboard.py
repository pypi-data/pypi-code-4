#!/usr/bin/env python
#--coding: utf8--
import sys

from jinja2 import Environment, PackageLoader

from pyscrum.loaders import RstLoader


def main():
    loader = RstLoader()
    board = loader.get_board(sys.argv[1])

    env = Environment(loader=PackageLoader('pyscrum'))

    template = env.get_template('board.html')
    print template.render(board=board).encode('utf-8')


if __name__ == '__main__':
    main()
