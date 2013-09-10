"""
This is the module for the versions command.
"""

__helpstr__ = """Usage: nodevers versions [options]

  Summary:
      Print all the installed versions

  Options:
      -h/--help         Print this text
      -a/--all          Display all installable versions

"""

import os
import sys
import getopt
import nodevers.shared as shared

def get_versions_list(display_all):
    """
    Return a list of all the installed Node versions.
    """
    if not display_all:
        versions_dir = shared.get_versions_dir()
        # os.path.isdir() will fail unless we do this.
        os.chdir(versions_dir)
        versions = [ver for ver in os.listdir(versions_dir) if os.path.isdir(ver)]
        return versions
    else:
        return shared.get_remote_versions_list()

def parse(args):
    """
    Parse the arguments and call the correct functions
    based on them.
    """
    display_all = False
    try:
        optlist, arglist = getopt.getopt(args, "ha", ["help", "all"])
    except getopt.error:
        err = sys.exc_info()[1]
        sys.stderr.write("Error: %s\n" % str(err))
        sys.exit(-1)
    for option, value in optlist:
        if option in ("-h", "--help"):
            shared.help_func(__helpstr__)
        elif option in ("-a", "--all"):
            display_all = True
    try:
        for v in get_versions_list(display_all):
            sys.stdout.write("%s\n" % v)
    except StandardError:
        err = sys.exc_info()[1]
        sys.stderr.write("Error: %s\n" % str(err))
        sys.exit(2)
