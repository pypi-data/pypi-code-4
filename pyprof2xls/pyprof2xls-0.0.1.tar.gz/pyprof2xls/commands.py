from modargs import args
import sys
import os
from pyprof2xls.generate import generate

prog='pyprof2xls'
mod=sys.modules[__name__]
default_cmd='generate'

def run():
    try:
        args.parse_and_run_command(sys.argv[1:], mod, default_command=default_cmd)
    except SystemExit:
        if len(sys.argv) == 1:
            help_command(on=default_cmd)
        else:
            help_command(on=sys.argv[1])

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
