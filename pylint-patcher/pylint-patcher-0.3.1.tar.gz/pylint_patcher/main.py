#!/usr/bin/env python
"""
main.py : Pylint Patcher main console script
"""
import sys
import argparse
import pylint.lint
from pylint_patcher import patcher, __version__

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
    parser.add_argument("--version", action="store_true")
    parsed_args, _ = parser.parse_known_args(args)

    if parsed_args.version:
        print "%s: %s" % (parser.prog, __version__)
        # Override sys.argv[0] for the Pylint version reporting
        sys.argv[0] = "pylint"

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
