"""
This is the module for the install command.
"""

import getopt
import sys
import nodevers.install_helper as install_helper
import nodevers.shared as shared

__helpstr__ = """Usage: nodevers install <version> [options]

  Summary:
      Install the specified version.

  Options:
      -h/--help         Print this text
      --buildargs       These will be passed to Node's configure script
      -l/--list         Display all installable versions

"""

def install(ver, build_args):
    """
    This calls the correct functions in the correct
    order to install Node.
    It also handles exceptions.
    """
    if shared.version_exists(ver):
        sys.stderr.write("Error: already installed: %s\n" % ver)
        sys.exit(1)
    try:
        nodesrc = install_helper.NodeSourceInstaller(ver,
                shared.get_version_dir(ver), build_args)
        sys.stdout.write("Downloading...\n")
        nodesrc.download()
        sys.stdout.write("Extracting...\n")
        nodesrc.extract()
        sys.stdout.write("Patching...\n")
        if len(shared.get_patches_list(ver)) == 0:
            sys.stdout.write("No patches found.\n")
        else:
            nodesrc.patch()
        sys.stdout.write("Configuring...\n")
        nodesrc.configure()
        sys.stdout.write("Building...\n")
        nodesrc.make()
        sys.stdout.write("Installing...\n")
        nodesrc.make_install()
    except StandardError:
        err = sys.exc_info()[1]
        sys.stderr.write("Error: %s\n" % str(err))
        sys.exit(2)
    finally:
        sys.stdout.write("Cleaning up...\n")
        try:
            nodesrc.cleanup()
        except StandardError:
            pass

def parse(args):
    """
    Parse the CLI options and call
    the correct functions based on them.
    """
    if len(args) == 0 or args[0] in ("-h", "--help"):
        shared.help_func(__helpstr__)
    elif args[0] in ("-l", "--list"):
        try:
            for v in shared.get_remote_versions_list():
                sys.stdout.write("%s\n" % v)
        except StandardError:
            err = sys.exc_info()[1]
            sys.stderr.write("Error: %s\n" % str(err))
            sys.exit(2)
    else:
        build_args = ""
        try:
            optlist, arglist = getopt.getopt(args[1:], "", ["buildargs="])
        except getopt.error:
            err = sys.exc_info()[1]
            sys.stderr.write("Error: %s\n" % str(err))
            sys.exit(-1)
        for option, value in optlist:
            if option in ("--buildargs"):
                build_args = value
        install(args[0], build_args)
