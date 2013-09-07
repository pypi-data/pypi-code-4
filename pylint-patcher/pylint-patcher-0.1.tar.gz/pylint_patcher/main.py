#!/usr/bin/env python
"""
main.py : Pylint Patcher main console script
"""
import sys
import pylint.lint
import pylint_patcher

def main(args=sys.argv[1:]):
    """
    Apply the patchfile containing the pylint ignores,
    then run the linter,
    then revert the patchfile changes.
    """
    # Apply the ignore patchfile before linting
    patcher = pylint_patcher.Patcher(args[0])
    patcher.patch()
    try:
        pylint.lint.Run(args)
    finally:
        # Revert the ignore patchfile
        patcher.unpatch()

if __name__ == "__main__": # pragma: no cover
    main()
