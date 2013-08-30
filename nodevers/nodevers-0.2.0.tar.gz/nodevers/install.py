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

"""

def install(ver, build_args):
    """
    This calls the correct functions in the correct
    order to install Node.
    It also handles exceptions.
    """
    if shared.version_exists(ver):
        sys.stderr.write("Error: %s is already installed\n" % ver)
        sys.exit(1)
    elif not shared.valid_version_string(ver):
        sys.stderr.write("Error: %s doesn't look like a valid version\n" % ver)
        sys.exit(2)
    try:
        node = install_helper.NodeInstaller(ver,
                shared.get_version_dir(ver), build_args)
        sys.stdout.write("Downloading...\n")
        node.download_source()
        sys.stdout.write("Extracting...\n")
        node.extract_source()
        sys.stdout.write("Patching...\n")
        if len(shared.get_patches_list(ver)) == 0:
            sys.stdout.write("No patches found.\n")
        else:
            node.patch()
        sys.stdout.write("Configuring...\n")
        node.configure()
        sys.stdout.write("Building...\n")
        node.make()
        sys.stdout.write("Installing...\n")
        node.make_install()
    except StandardError:
        err = sys.exc_info()[1]
        sys.stderr.write("Error: %s\n" % str(err))
        sys.exit(2)
    finally:
        sys.stdout.write("Cleaning up...\n")
        try:
            node.cleanup()
        except StandardError:
            pass

def parse(args):
    """
    Parse the CLI options and call
    the correct functions based on them.
    """
    if len(args) == 0 or args[0] in ("-h", "--help"):
        shared.help_func(__helpstr__)
    else:
        build_args = ""
        try:
            optlist, arglist = getopt.getopt(args[1:], "h", ["help",
                "buildargs="])
        except getopt.error:
            err = sys.exc_info()[1]
            sys.stderr.write("Error: %s\n" % str(err))
            sys.exit(-1)
        for option, value in optlist:
            if option in ("-h", "--help"):
                shared.help_func(__helpstr__)
            elif option in ("--buildargs"):
                build_args = value
        install(args[0], build_args)
