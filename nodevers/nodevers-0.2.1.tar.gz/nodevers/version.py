"""
This is the module for the version command.
"""

__helpstr__ = """Usage: nodevers version [options]

  Summary:
      Print the currently active version

  Options:
      -h/--help         Print this text

"""

import re
import subprocess
import sys
import getopt
import nodevers.shared as shared


def parse(args):
    """
    Parse the arguments and call the correct functions
    based on them.
    """
    if len(args) == 0:
        try:
            ver = shared.current_version()
            sys.stdout.write("%s\n" % ver)
        except OSError:
            sys.stderr.write("Error: there is no currently active Node\n")
    else:
        try:
            optlist, arglist = getopt.getopt(args, "h", ["help"])
        except getopt.error:
            err = sys.exc_info()[1]
            sys.stderr.write("Error: %s\n" % str(err))
            sys.exit(-1)
        for option, value in optlist:
            if option in ("-h", "--help"):
                shared.help_func(__helpstr__)
