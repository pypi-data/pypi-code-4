"""
This checks if nodevers prefix exists
and then calls cli.parse().
"""
import sys

from . import misc
from . import cli

if not misc.valid_nodevers_prefix(misc.get_nodevers_prefix()):
    try:
        misc.mknodevers_prefix(misc.get_nodevers_prefix())
    except IOError:
        sys.stderr.write("Error: failed to create the nodevers directory")
        sys.exit(3)

def main(argv):
    cli.parse(argv[1:])

if __name__ == "__main__":
    main(sys.argv)
