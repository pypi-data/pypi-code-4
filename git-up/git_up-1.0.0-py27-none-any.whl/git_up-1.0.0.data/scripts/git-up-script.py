#!python
# EASY-INSTALL-ENTRY-SCRIPT: 'git-up==1.0.0','console_scripts','git-up'
__requires__ = 'git-up==1.0.0'
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.exit(
        load_entry_point('git-up==1.0.0', 'console_scripts', 'git-up')()
    )
