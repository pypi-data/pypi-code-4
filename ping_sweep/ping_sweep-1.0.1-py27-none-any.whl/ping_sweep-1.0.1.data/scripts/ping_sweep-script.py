#!python
# EASY-INSTALL-ENTRY-SCRIPT: 'ping-sweep==1.0.1','console_scripts','ping_sweep'
__requires__ = 'ping-sweep==1.0.1'
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.exit(
        load_entry_point('ping-sweep==1.0.1', 'console_scripts', 'ping_sweep')()
    )
