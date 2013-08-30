"""
This is the module for the use command.
"""

__helpstr__ = """Usage: nodevers use <version> [options]

  Summary:
      Makes the specified Node version the default

  Options:
      -h/--help         Print this text

"""

import os
import sys
import getopt
import nodevers.shared as shared


def parse(args):
    """
    Parse the arguments and call the correct functions
    based on them.
    """
    if len(args) == 0 or args[0] in ("-h", "--help"):
        shared.help_func(__helpstr__)
    else:
        try:
            optlist, arglist = getopt.getopt(args[1:], "h", ["help"])
        except getopt.error:
            err = sys.exc_info()[1]
            sys.stderr.write("Error: %s\n" % str(err))
            sys.exit(-1)
        for option, value in optlist:
            if option in ("-h", "--help"):
                shared.help_func(__helpstr__)
        try:
            shared.link_to(args[0])
        except shared.NoSuchVersionError:
            err = sys.exc_info()[1]
            sys.stdout.write("Error: %s\n" % str(err))
