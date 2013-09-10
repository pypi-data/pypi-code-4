"""
This checks if nodevers prefix exists
and then calls cli.parse().
"""
import sys

import nodevers.shared as shared
import nodevers.cli as cli

if not shared.valid_nodevers_prefix(shared.get_nodevers_prefix()):
    try:
        shared.mknodevers_prefix(shared.get_nodevers_prefix())
    except IOError:
        sys.stderr.write("Error: failed to create the nodevers directory")
        sys.exit(3)

def main(argv):
    try:
        cli.parse(argv[1:])
    except KeyboardInterrupt:
        sys.exit(1)

if __name__ == "__main__":
    main(sys.argv)
