import sys
import argparse
import unittest
import collections


__version__ = '0.0.0'


class Error(Exception):
    pass


def p(v):
    print(v, file=sys.stderr)
    return v


def flatten(vs):
    """
    # Flatten containers

    ## Note
    Do not include recursive elements.

    ## Exceptions
    - `RuntimeError`: Recursive elements will cause this
    """
    if isinstance(vs, str):
        yield vs
    else:
        for v in vs:
            if isinstance(v, collections.abc.Iterable):
                yield from flatten(v)
            else:
                yield v


def list_2d(n_row, n_column):
    assert n_row >= 1
    assert n_column >= 1

    return [[None
             for _
             in range(n_column)]
            for _
            in range(n_row)]


class TestAction(argparse.Action):
    def __init__(self,
                 option_strings,
                 dest=argparse.SUPPRESS,
                 default=argparse.SUPPRESS,
                 help=None):
        super().__init__(option_strings=option_strings,
                         dest=dest,
                         default=default,
                         nargs=0,
                         help=help)


    def __call__(self, parser, namespace, values, option_string=None):
        unittest.main(argv=sys.argv[:1])
        parser.exit()


class _Tester(unittest.TestCase):
    def test_list_2d(self):
        self.assertEqual(list_2d(2, 3),
                         [[None, None, None],
                          [None, None, None]])

    def test_flatten(self):
        self.assertEqual(list(flatten([])), [])
        self.assertEqual(list(flatten([1, 2])), [1, 2])
        self.assertEqual(list(flatten([1, [2, 3]])), [1, 2, 3])
        self.assertEqual(list(flatten(['ab'])), ['ab'])
        self.assertEqual(tuple(sorted(flatten((1, 2, (3, [4, set([5, 6]), 7 ], [8, 9]))))),
                         tuple(sorted((1, 2, 3, 4, 5, 6, 7, 8, 9))))


def _parse_arguments(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='Read a simple Makefile and write a dot file')
    parser.add_argument('--test',
                        action=TestAction,
                        help='run tests')
    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s {version}'.format(version=__version__))

    return parser.parse_args(args)


def main(args=sys.argv[1:]):
    _parse_arguments(args)


if __name__ == '__main__':
    main(sys.argv[1:])
