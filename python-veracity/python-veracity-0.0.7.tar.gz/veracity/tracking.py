#!/usr/bin/env python

"""
Initializes Veracity's distributed build tracking feature.
"""

import sys
import argparse
import logging

from veracity import TRACKING, VERSION
from veracity import common


def run(config, init=False):
    """Run a house-keeping command for build tracking.
    @param config: common Config object
    @param init: initialize repos with a default build configuration
    """
    print(config, init)
    return True  # TODO: implement function


# TODO: share the common logic with tracking, builder, and poller
def main():  # pragma: no cover - tested manually
    """Process command-line arguments and run the program.
    """
    # Main parser
    parser = argparse.ArgumentParser(prog=TRACKING, description=__doc__, formatter_class=common.formatter_class)
    parser.add_argument('-V', '--version', action='version', version=VERSION)
    parser.add_argument('-v', '--verbose', action='count', help="enable verbose logging")
    parser.add_argument('repo', nargs='*', help="repository names")
    parser.add_argument('-c', '--config', metavar='PATH', help="path to a configuration file")
    parser.add_argument('--no-config', action='store_true', help="ignore local configuration files")
    parser.add_argument('--init', action='store_true', help="initialize with a default build configuration")

    # Parse arguments
    args = parser.parse_args()

    # Configure logging
    common.configure_logging(args.verbose)

    # Parse the configuration file
    config = common.parse_config(args.config, not args.no_config, parser.error, repos=args.repo)

    # Ensure we are running as the correct user
    common.check_user(args.daemon, parser.error)

    # Run the program
    success = False
    try:
        success = run(config, init=args.init)
    except KeyboardInterrupt:  # pylint: disable=W0703
        logging.debug("cancelled manually")
    if not success:
        sys.exit(1)


if __name__ == '__main__':  # pragma: no cover - tested manually
    main()
