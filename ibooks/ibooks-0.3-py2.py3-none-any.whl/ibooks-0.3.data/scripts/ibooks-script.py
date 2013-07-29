#!python
# EASY-INSTALL-ENTRY-SCRIPT: 'ibooks==0.3','console_scripts','ibooks'
__requires__ = 'ibooks==0.3'
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.exit(
        load_entry_point('ibooks==0.3', 'console_scripts', 'ibooks')()
    )
