from argparse import Action, ArgumentError, ArgumentParser, RawTextHelpFormatter

class RangeAction(Action):
    def __call__(self, parser, namespace, values, option_string=None):

        def assert_integer(value):
            try:
                int(value)
            except Exception:
                raise ArgumentError(self, "%s is not an Integer." % value)

        start = 1
        stop = 1

        if "," in values:
            if values.startswith(",") or values.endswith(","):
                raise ArgumentError(self, "Complete range not provided. " + values)
            else:
                start, stop = values.split(",")
                assert_integer(start)
                assert_integer(stop)
                start, stop = int(start), int(stop)
        else:
            assert_integer(values)
            stop = int(values)

        if stop < start:
            raise ArgumentError(self, "Range End %s is less than Range Start %s" % (stop, start))

        setattr(namespace, self.dest, [start, stop+1])

def _parse_args():
    parser = ArgumentParser(
        description="MiProMan - iTerm2 Profiles Manager for Humans!",
        formatter_class=RawTextHelpFormatter,
        add_help=True,
    )
    parser.add_argument(
        dest="servers",
        nargs="+",
        help="Servers to create profiles for.\nCan use the form server{0:02d} with the range flag to add a range of servers.\nSkips if server already exists.",
    )
    parser.add_argument(
        "-c",
        "--command",
        dest="command",
        help="The command to run for each profile.\nUse {0} to refernce the server name in the command.\nDefault: ssh {0}",
    )
    parser.add_argument(
        "-t",
        "--tags",
        dest="tags",
        nargs="*",
        help="Tags for the profiles.",
    )
    parser.add_argument(
        "-r",
        "--range",
        dest="range",
        action=RangeAction,
        metavar="STOP | START,STOP",
        help="If server uses range format add profiles for specified range.\nCan be provided as a single number or comma separated pair.\nIf single value range starts from 1.\nEx. server{0:02d} -r 4 => server01 - server04\nEx. server{0:02d} -r 10,20 => server10 - server20",
    )
    parser.add_argument(
        "-p",
        "--profile",
        dest="profile",
        metavar="FILE",
        help="iTerm2 profile plist.\nDefault: $HOME/Library/Preferences/com.googlecode.iterm2.plist",
    )
    parser.add_argument(
        "-n",
        "--template",
        dest="template_name",
        help="iTerm2 profile name to be used as base template for new server entries.\nTemplate is required to add new profiles.\nDefault: Default",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action="store_true",
        help="Increase output verbosity.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="Version: 0.1",
    )

    return parser.parse_args()._get_kwargs()

