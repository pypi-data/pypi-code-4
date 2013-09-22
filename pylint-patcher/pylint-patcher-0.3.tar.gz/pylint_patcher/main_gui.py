#!/usr/bin/env python
"""
main-gui.py : Pylint Patcher GUI
"""
import sys
from pylint_patcher.external.pylint import gui

def main(args=sys.argv[1:]):
    """
    Run the Pylint GUI
    """
    gui.Run(args)

if __name__ == "__main__": # pragma: no cover
    main()
