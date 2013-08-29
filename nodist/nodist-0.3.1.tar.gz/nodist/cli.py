import sys
import os
from . import misc
from . import installer

# We may need these in future.
# if sys.hexversion < 34013424: # Python 2.7.0
#     import optparse
# else:
#     import argparse

def parse(args):
    version = args[0]
    if len(args) == 1:
        if misc.version_exists(version):
            switch_to(version)
        else:
            installer.create_installation(version)
            switch_to(version)
    else:
        if '-l' in args or '--log' in args and not misc.version_exists(version):
            installer.create_installation(version, True)
        elif '-d' in args or '--delete' in args:
            installer.delete_installation(version)

def switch_to(version):
    version_bin_path = os.path.join(misc.get_version_path(version), "bin")
    link_path = misc.get_bin_path()
    if os.path.lexists(link_path):
        os.unlink(link_path)
    os.symlink(version_bin_path, link_path)
