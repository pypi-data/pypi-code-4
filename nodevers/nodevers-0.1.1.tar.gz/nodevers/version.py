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
from . import cli

def current_version():
    """
    Try to get the current version.
    """
    # We'll let parse() handle the exceptions.
    process = subprocess.Popen(["node", "-v"], stdout=subprocess.PIPE)
    node_output = process.stdout.read()
    regex = "v(\d+\.\d+\.\d+)"
    match = re.match(regex, node_output)
    ver = match.group(1)
    return ver

def parse(args):
    """
    Parse the arguments and call the correct functions
    based on them.
    """
    if len(args) == 0:
        try:
            ver = current_version()
            sys.stdout.write("%s\n" % ver)
        except OSError:
            sys.stderr.write("There is no currently active Node.\n")
    else:
        try:
            optlist, arglist = getopt.getopt(args, "h", ["help"])
        except getopt.error:
            err = sys.exc_info()[1]
            sys.stderr.write("Error: %s\n" % str(err))
            sys.exit(-1)
        for option, value in optlist:
            if option in ("-h", "--help"):
                cli.help_func(__helpstr__)
