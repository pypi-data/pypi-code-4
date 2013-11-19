#!/usr/bin/env python

"""
A "builder" for Veracity's distributed build tracking feature.
"""

import os
import sys
import time
import shutil
import argparse
import tempfile
import subprocess
from collections import defaultdict
import logging

from veracity import BUILDER, VERSION
from veracity.objects import _BaseRepositoryObject
from veracity import common
from veracity import settings

VIRTUALENV = BUILDER + '-env'


class Builder(_BaseRepositoryObject):
    """Represents a builder for a particular repository."""

    def __init__(self, repo, config):
        """Represent a tag.
        @param repo: repository name
        @param config: common Config object
        """
        super().__init__(repo=repo, create=False)
        self.config = config
        self.count = 0
        self.stats = defaultdict(int)

    def __repr__(self):
        return self._repr(self.repo, self.config)

    def __str__(self):
        return "'{r}' builder".format(r=self.repo)

    def __eq__(self, other):
        if not isinstance(other, Builder):
            return False
        else:
            return all((super().__eq__(other),
                        self.config.environments == other.config.environments))

    def __ne__(self, other):
        return not self == other

    def run(self):
        """Perform one build iteration.
        """
        for environment in self.config.environments:
            for status in self.config.starts:

                # Look for a build request
                request = self.repo.get_build(environment, status)
                if not request:
                    time.sleep(settings.BUILD_DELAY)
                    continue

                # Check out build request's changeset
                logging.info("found build request: {0} in {1}".format(request, request.repo))
                self.count += 1
                temp = tempfile.mkdtemp()
                logging.debug("directory for checkout: {0}".format(temp))
                with self.repo.checkout(temp, rev=request.changeset.rev) as work:

                    # Update the configuration from the changeset
                    work.chdir()
                    path = common.find_config(work.path, walk=True)
                    if path:
                        logging.info("updating the build configuration from the changeset...")
                        self.config.update(path)

                    # Create a virtual environment
                    logging.info("initial build state: [{0}]".format(status))
                    work.chdir()
                    self.create_virtualenv()

                    # Build loop
                    try:
                        while True:

                            # Enter the next build state
                            request.update(self.config.next(request.status))

                            # Run the command for the current state
                            path, command = self.config.get_build(request.status)
                            work.chdir()
                            success = self.call(path, command)

                            # Process the command results
                            if success:
                                request.update(self.config.exit(request.status))
                            else:
                                request.update(self.config.fail(request.status))
                            if request.status in self.config.ends:
                                break

                    except ValueError as error:
                        logging.warning(error)
                        logging.critical("deleting build request due to invalid configuration: {0}".format(request))
                        request.delete()

                # Build completed
                self.stats[request.status] += 1
                logging.info("completed builds: {0}".format(self.count))

    def test(self, single=None):
        """Perform one build iteration locally as a test.
        """
        for status in ([single] if single else self.config.starts):

            # Create a virtual environment
            logging.info("initial build state: [{0}]".format(status))
            self.create_virtualenv()

            # Build loop
            while True:

                # Enter the next build state
                if not single:
                    status = self.config.next(status)

                # Run the command for the current state
                path, command = self.config.get_build(status)
                success = self.call(path, command)

                # Process the command results
                if success:
                    status = self.config.exit(status)
                else:
                    status = self.config.fail(status)
                if single or status in self.config.ends:
                    break

            # Delete the virtual environment
            self.delete_virtualenv()

    def create_virtualenv(self):
        """Create a virtual environment for the build.
        """
        if self.config.virtualenv:
            logging.info("creating a virtual environment for build...")
            command = "virtualenv {0}".format(VIRTUALENV)
            logging.info("$ {0}".format(command))
            subprocess.call(command, shell=True)

    def delete_virtualenv(self):
        """Delete the created virtual environment.
        """
        if self.config.virtualenv:
            logging.info("deleting the virtual environment...")
            shutil.rmtree(VIRTUALENV)

    def call(self, path, command):
        """Run a build command in the current directory.
        @param command: shell string
        @return: indicates command returned no error
        """
        if command:
            if path:
                command = "cd {p} && {c}".format(p=path, c=command)
            if self.config.virtualenv:
                if os.name == 'nt':
                    command = "{v}\\Scripts\\activate && {c}".format(v=VIRTUALENV, c=command)
                else:
                    command = ". {v}/bin/activate && {c}".format(v=VIRTUALENV, c=command)
            logging.info("$ {0}".format(command))
            return subprocess.call(command, shell=True) == 0
        else:
            logging.info("$ (no command)")
            return True


def run(config, daemon=False, test=False):
    """Run a builder for each repository.
    @param config: common Config object
    @param daemon: run as a daemon
    @param test: run locally as a test
    @return: indicates builder(s) ran successfully
    """
    builders = [Builder(repo, config.copy()) for repo in config.repos]
    if not builders:
        return False

    while True:
        for builder in builders:
            if isinstance(test, str):
                logging.info("testing [{s}] of {b}...".format(b=builder, s=test))
                builder.test(single=test)
            elif test:
                logging.info("testing {b}...".format(b=builder))
                builder.test()
            else:
                logging.log(logging.DEBUG if daemon else logging.INFO,
                            "running {b}...".format(b=builder))
                builder.run()
        if not daemon or test:
            break

    return True


# TODO: share the common logic with tracking, builder, and poller
def main():  # pragma: no cove, tested by integration tests
    """Process command-line arguments and run the program.
    """
    # Main parser
    parser = argparse.ArgumentParser(prog=BUILDER, description=__doc__,
                                     formatter_class=common.formatter_class)
    parser.add_argument('-V', '--version', action='version', version=VERSION)
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help="enable verbose logging")
    parser.add_argument('-d', '--daemon', action='store_true',
                        help="keep the process running")
    parser.add_argument('-t', '--test', metavar='ALIAS', nargs='?', const=True,
                        help="dry run locally as a test")
    parser.add_argument('repo', nargs='*', help="repository names")
    parser.add_argument('--config', metavar='PATH',
                        help="path to a configuration file")
    parser.add_argument('--no-config', action='store_true',
                        help="ignore local configuration files")
    parser.add_argument('--env', metavar='ALIAS',
                        help="environment alias for this machine")

    # Parse arguments
    args = parser.parse_args()

    # Configure logging
    common.configure_logging(args.verbose)

    # Parse the configuration file
    config = common.parse_config(args.config, not args.no_config, parser.error,
                                 repos=args.repo, envs=[args.env] if args.env else None)
    if not config.repos:
        parser.error("specify at least one repository")
    if len(config.environments) != 1 and not args.test:
        parser.error("specify exactly one environment alias for this machine")

    # Ensure we are running as the correct user
    common.check_user(args.daemon, parser.error)

    # Run the program
    success = False
    try:
        success = run(config, args.daemon, args.test)
    except KeyboardInterrupt:  # pylint: disable=W0703
        logging.debug("cancelled manually")
    if not success:
        sys.exit(1)


if __name__ == '__main__':  # pragma: no cover, tested by integration tests
    main()
