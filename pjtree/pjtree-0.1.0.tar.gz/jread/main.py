# -*- utf-8 -*-


def main():
    u""" Main method

    main method.
    """
    import argparse
    from . import jread

    parser = argparse.ArgumentParser()
    jread.set_argument(parser)
    args = parser.parse_args()
    data = jread.scan({}, args.path, args.encoding)
    if args.file is None:
        jread.show(data)
    else:
        jread.save(data, args.file, args.encoding)


if __name__ == '__main__':
    main()
