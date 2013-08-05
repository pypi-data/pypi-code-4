from modargs import args
import sys
import os
from pyprof2xls.generate import generate
from pyprof2xls.version import PYPROF2XLS_VERSION

prog='pyprof2xls'
mod=sys.modules[__name__]
default_cmd='generate'

def print_prof_help_and_exit():
    print "\nYou need to specify prof files using the --prof option. Here is the help:\n"
    help_command(on=default_cmd)
    sys.exit(1)

def run():
    # temp: Check if someone does the intuitive thing and help.
    if len(sys.argv) > 1:
        if ".prof" in sys.argv[1]:
            print_prof_help_and_exit()
        elif len(sys.argv) > 2:
            if sys.argv[1] == 'generate' and '.prof' in sys.argv[2]:
                print_prof_help_and_exit()

    try:
        args.parse_and_run_command(sys.argv[1:], mod, default_command=default_cmd)
    except SystemExit:
        print "For help run: pyprof2xls help"

def version_command():
    print "pyprof2xls version %s" % PYPROF2XLS_VERSION

def help_command(on=False):
    """
    Prints this help.
    """
    args.help_command(prog, mod, default_cmd, on)

def generate_command(
        prof=None, # Path to .prof file to process.
        xls=False # Custom filename for .xls output.
    ):
    """
    Generates an .xls file from the specified cProfile output file.

    .xls files can be opened with https://www.libreoffice.org/
    """
    if not xls:
        xls = "%s.xls" % os.path.splitext(prof)[0]
    generate(prof, xls)
    print "%s generated" % xls
