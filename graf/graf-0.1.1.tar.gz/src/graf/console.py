#!/usr/bin/env python
# coding=utf-8
"""
Console program of graf

(C) 2013 hashnote.net, Alisue
"""
__author__  = 'Alisue (lambdalisue@hashnote.net)'
__version__ = '0.1.0'
__date__    = '2013-10-08'


def main(args=None):
    """
    Execute graf console program
    """
    import graf
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-i', '--interactive', default=False,
        action='store_true',
        help="Drop to interactive shell after running file instead of exiting")
    parser.add_argument('script_files', nargs='*')
    # parse argument
    args = parser.parse_args(args)

    # call all script files
    for script_file in args.script_files:
        graf.call(script_file)

    # enable interactive shell if no script_files was specified
    if len(args.script_files) == 0:
        args.interactive = True

    # drop to interactive shell if required
    if args.interactive:
        try:
            import readline # optional, will allow Up/Down/History in the console
        except ImportError:
            pass
        import code
        # create global variables
        local = globals().copy()
        # extend graf commands in local
        graf.use(local)
        code.interact(local=local)

if __name__ == '__main__':
    main()
