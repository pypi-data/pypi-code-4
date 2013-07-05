import sys
import argparse

from csat.graphml.builder import merge_files


def merge():
    parser = argparse.ArgumentParser('csat-merge')
    parser.add_argument('file1', metavar='file', nargs=1)
    parser.add_argument('files', metavar='file', nargs='+')
    parser.add_argument('-o', '--output', default='-', help='Path to the '
                            'resulting GraphML file. A single - makes the '
                            'graph to be written to stdout. The default is to'
                            ' write the graph to stdout.')
    args = parser.parse_args()

    d = merge_files(args.file1 + args.files)

    #, key=('domain', {
    #    'people': ('email', None),
    #    'components': ('package', None),
    #}))

    if args.output == '-':
        d.to_file(sys.stdout)
    else:
        with open(args.output, 'w') as fh:
            d.to_file(fh)
