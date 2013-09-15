# -*- utf-8 -*-


def main():
    u""" Main method

    main method.
    """
    import os
    import argparse
    from . import jwrite

    parser = argparse.ArgumentParser()
    jwrite.set_argument(parser)
    args = parser.parse_args()
    try:
        data = jwrite.load_json(args.json, args.encoding)
    except ValueError:
        print('can not laod file!')
        sys.exit(1)

    if args.force and args.notoverwrite:
        args.force = False

    if os.access(os.path.dirname(os.path.abspath(args.path)), os.W_OK):
        jwrite.trace(data, args.path, owrite=args.force, nowrite=args.notoverwrite)
    else:
        print('can not make files!')


if __name__ == '__main__':
    main()
