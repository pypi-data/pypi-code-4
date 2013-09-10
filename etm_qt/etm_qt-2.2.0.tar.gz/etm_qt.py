#!/usr/bin/env python
import os, sys

lib_path = os.path.relpath('etmQt/')
sys.path.append(lib_path)

import etmQt.v as v
import etmQt.etmData as etmData
import etmQt.etmView as etmView
import etmQt.etm_rc as etm_rc

if __name__ == "__main__":
    etmdir = ''
    etm = sys.argv[0]
    if (len(sys.argv) > 1 and os.path.isdir(sys.argv[1])):
        etmdir = sys.argv.pop(1)
    if (len(sys.argv) > 1 and sys.argv[1] in
        ['a', 'c', 'l', 'm', 's', '?', 'help']):
        if len(sys.argv) == 2 and sys.argv[1] in ['?', 'help']:
            print("""\
Usage:

    etm_qt.py [path] [acms?l]

With no arguments, etm will use settings from the
configuration file ~/.etm/etm.cfg and open the GUI.

If the first argument is the path to a directory
which contains a file named etm.cfg, then settings
from that file will be used instead.

If the first argument, other than the optional path,
is either "a", "c", "m", "s", "?" or "l" (lower case
L), then the remaining arguments will be executed by
etm without opening the GUI.

- a: display an action report using the remaining
     arguments as the report specification.
- c: display a custom report using the remaining
     arguments as the report specification.
- m: display a report using the remaining argument,
     which must be a positive integer, to display a
     report using the corresponding entry from the
     file given by report_specifications in etm.cfg.
     Use ? m or m ? to display the numbered list of
     entries from this file.
- s: display the next few days from the day view
     combined with any items in the now and next
     views. This command uses no further arguments.
- ?: display (this) command line help information or,
     if followed by a, c, m or s, then display help
     information about the specified command.
- l: begin an interactive shell loop in which the above
     commands are available and can be adjusted and
     run again without reloading the data files.
    """)
        else:
            etmData.main(etmdir, sys.argv)
    else:
        etmView.main(etmdir)

