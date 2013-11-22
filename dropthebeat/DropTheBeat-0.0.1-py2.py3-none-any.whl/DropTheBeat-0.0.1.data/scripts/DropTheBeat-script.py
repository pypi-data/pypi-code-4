#!python
# EASY-INSTALL-ENTRY-SCRIPT: 'DropTheBeat==0.0.1','console_scripts','DropTheBeat'
__requires__ = 'DropTheBeat==0.0.1'
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.exit(
        load_entry_point('DropTheBeat==0.0.1', 'console_scripts', 'DropTheBeat')()
    )
