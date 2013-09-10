"""
This is the module for the remove command.
"""

__helpstr__ = """Usage: nodevers remove <version> [options]

  Summary:
      Uninstalls the specified Node version

  Options:
      -h/--help         Print this text

"""

import shutil
import sys
import getopt
import nodevers.shared as shared

def remove(ver):
    """
    Uninstalls the specified version.
    """
    if ver == shared.current_version():
        shared.link_to("system")
    shutil.rmtree(shared.get_version_dir(ver))

def parse(args):
    """
    Parse the arguments and call the correct functions
    based on them.
    """
    if len(args) == 0 or args[0] in ("-h", "--help"):
        shared.help_func(__helpstr__)
    else:
        try:
            optlist, arglist = getopt.getopt(args[1:],"")
        except getopt.error:
            err = sys.exc_info()[1]
            sys.stderr.write("Error: %s\n" % str(err))
            sys.exit(-1)
        if shared.version_exists(args[0]):
            remove(args[0])
        else:
            sys.stdout.write("Error: no such version installed\n")
