#!python
# EASY-INSTALL-ENTRY-SCRIPT: 'python-veracity==0.0.10','console_scripts','vv-tracking'
__requires__ = 'python-veracity==0.0.10'
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.exit(
        load_entry_point('python-veracity==0.0.10', 'console_scripts', 'vv-tracking')()
    )
