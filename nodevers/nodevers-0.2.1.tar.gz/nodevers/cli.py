"""
This module connects everything together.
It calls the correct command based on the arguments passed to its
parse() function.
"""

import sys
import nodevers
import nodevers.shared as shared
import nodevers.version as version
import nodevers.versions as versions
import nodevers.install as install
import nodevers.use as use
import nodevers.remove as remove

__helpstr__ = """nodist %s
Usage: nodist <command> [options]

  Commands:
      install           Install a Node
      use               Make the specified Node version the default
      versions          List all the currently installed versions
      help              Print this
      remove            Uninstall the specified Node version

""" % nodevers.__version__


def parse(args):
    """
    Parse the CLI options and call
    the correct functions based on them.
    """
    known_commands = ("version", "versions", "install", "help",
            "use", "remove")
    if len(args) == 0:
        shared.help_func(__helpstr__)
    elif args[0] == "help" or args[0] == "-h" or args[0] == "--help":
        shared.help_func(__helpstr__)
    elif args[0] == "-v" or args[0] == "--version":
        sys.stdout.write("nodevers %s\n" % nodevers.__version__)
    elif args[0] not in known_commands:
        sys.stderr.write("Error: unrecognized command: '%s'\n" %
                args[0])
        sys.exit(-1)
    if args[0] == "version":
        version.parse(args[1:])
    elif args[0] == "versions":
        versions.parse(args[1:])
    elif args[0] == "install":
        install.parse(args[1:])
    elif args[0] == "use":
        use.parse(args[1:])
    elif args[0] == "remove":
        remove.parse(args[1:])
