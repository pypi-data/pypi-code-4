# (c) 2005 Ian Bicking and contributors; written for Paste
# (http://pythonpaste.org) Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php

import sys


def main(argv=sys.argv, quiet=False):
    print("GinsFsm, the asynchronous framework based in finite-state machines")
    print("Available Commands:")
    print("  - ginsfsm-help: This mini help.")
    print("  - gcreate: Render GinsFSM scaffolding to an output directory.")
    print("  - gserve: Run a GinsFSM application.")
    print("  - gconsole: Console to connect to a GinsFSM application.")
