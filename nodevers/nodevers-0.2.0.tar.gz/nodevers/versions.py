"""
This is the module for the versions command.
"""

__helpstr__ = """Usage: nodevers versions [options]

  Summary:
      Print all the installed versions

  Options:
      -h/--help         Print this text

"""

import os
import sys
import getopt
import nodevers.shared as shared

def get_versions_list():
    """
    Return a list of all the installed Node versions.
    """
    versions_dir = shared.get_versions_dir()
    # os.path.isdir() will fail unless we do this.
    os.chdir(versions_dir)
    versions = [ver for ver in os.listdir(versions_dir) if os.path.isdir(ver)]
    return versions

def parse(args):
    """
    Parse the arguments and call the correct functions
    based on them.
    """
    if len(args) == 0:
        for ver in get_versions_list():
            sys.stdout.write("%s\n" % ver)
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
