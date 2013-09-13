# -*- utf-8 -*-


def main():
    u""" Main method

    main method.
    """
    import argparse
    import jwrite

    parser = argparse.ArgumentParser()
    jwrite.set_argument(parser)
    args = parser.parse_args()
    data = jwrite.load_json(args.json, args.encoding)
    if args.force and args.notoverwrite:
        args.force = False
    jwrite.trace(data, args.path, owrite=args.force, nowrite=args.notoverwrite)


if __name__ == '__main__':
    main()
