"""htpasswd-cli

Usage:
  htpasswd-cli <password>
  htpasswd-cli --version

Options:
  --version     Show version.

"""

import sys
from docopt import docopt
from htpasswd import basic

from htpasswdcli import __version__ 


def main():
    argument = docopt(__doc__, version=__version__)
    password = argument.get('<password>') 
    sys.stdout.write(basic.Basic(None)._crypt_password(password) + "\n")


if __name__ == '__main__':
    main() 
