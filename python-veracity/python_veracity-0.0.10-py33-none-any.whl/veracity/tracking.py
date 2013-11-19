#!/usr/bin/env python

"""
Initializes Veracity's distributed build tracking feature.
"""

import sys
import argparse
import logging

from veracity import TRACKING, VERSION
from veracity import common
from veracity import vv
from veracity import vscript
from veracity.objects import Repository, BuildRequest


def run(name, initialize=False, delete_build=None):
    """Run a house-keeping command for build tracking.
    @param name: repository name
    @param initialize: initialize repos with a default build configuration
    @param delete_build: BID to delete
    @return: indication of success
    """
    try:
        repo = Repository(name)
        repo.pull()
        if initialize:
            logging.info("initializing builds for '{0}'...".format(repo))
            vscript.init_builds(repo)
        if delete_build == 'all':
            del repo.builds
        elif delete_build:
            request = BuildRequest(delete_build, None, repo=repo)
            request.delete()

    except (vv.VeracityException, vscript.VeracityScriptException) as exc:
        logging.error(exc)
        return False

    else:
        repo.push()
        return True


# TODO: share the common logic with tracking, builder, and poller
def main():  # pragma: no cover, tested by integration tests
    """Process command-line arguments and run the program.
    """
    # Main parser
    parser = argparse.ArgumentParser(prog=TRACKING, description=__doc__,
                                     formatter_class=common.formatter_class)
    parser.add_argument('-V', '--version', action='version', version=VERSION)
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help="enable verbose logging")
    parser.add_argument('repo', help="repository name")
    parser.add_argument('--initialize', action='store_true',
                        help="initialize a default build configuration")
    parser.add_argument('--delete-build', metavar='BID', nargs='?',
                        const='all', help="delete a build request")

    # Parse arguments
    args = parser.parse_args()
    if args.delete_build == 'all':
        if input("Type 'all' to delete all builds: ") != 'all':
            parser.error("confirmation not provided to delete all builds")

    # Configure logging
    common.configure_logging(args.verbose)

    # Ensure we are running as the correct user
    common.check_user(False, parser.error)

    # Run the program
    success = False
    try:
        success = run(args.repo,
                      initialize=args.initialize,
                      delete_build=args.delete_build)
    except KeyboardInterrupt:  # pylint: disable=W0703
        logging.debug("cancelled manually")
    if not success:
        sys.exit(1)


if __name__ == '__main__':  # pragma: no cover, tested by integration tests
    main()
