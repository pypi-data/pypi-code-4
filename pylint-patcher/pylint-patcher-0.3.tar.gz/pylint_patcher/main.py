#!/usr/bin/env python
"""
main.py : Pylint Patcher main console script
"""
import sys
import argparse
import pylint.lint
from pylint_patcher import patcher

class ArgumentParser(argparse.ArgumentParser):
    """Override the error handler to ignore all errors"""
    def error(self, message):
        """Override the error handler to ignore all errors"""
        pass

def main(args=sys.argv[1:], **kwds):
    """
    Apply the patchfile containing the pylint ignores,
    then run the linter,
    then revert the patchfile changes.
    """
    # Attempt to parse the Pylint target
    parser = ArgumentParser(add_help=False)
    parser.add_argument("target")
    parsed_args, _ = parser.parse_known_args(args)

    if parsed_args.target is None:
        # No target, so just print the Pylint usage docs
        pylint.lint.Run(args, **kwds)
        return

    # Apply the ignore patchfile before linting
    patch = patcher.Patcher(parsed_args.target)
    patch.patch()
    try:
        pylint.lint.Run(args, **kwds)
    finally:
        # Revert the ignore patchfile
        patch.unpatch()

if __name__ == "__main__": # pragma: no cover
    main()
