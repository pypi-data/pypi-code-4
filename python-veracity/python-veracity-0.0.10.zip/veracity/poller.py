#!/usr/bin/env python

"""
A "poller" for Veracity's distributed build tracking feature.
"""

import sys
import time
import argparse
import tempfile
import subprocess
from collections import defaultdict
import logging

from veracity import POLLER, VERSION
from veracity import common
from veracity import settings
from veracity.objects import _BaseRepositoryObject


class Poller(_BaseRepositoryObject):
    """Represents a poller for a particular repository."""

    def __init__(self, repo, config):
        """Represent a tag.
        @param repo: repository name
        @param config: common Config object
        """
        super().__init__(repo=repo, create=False)
        self.config = config
        self.count = 0
        self.times = defaultdict(float)

    def __repr__(self):
        return self._repr(self.repo, self.config)

    def __str__(self):
        return "'{r}' poller".format(r=self.repo)

    def __eq__(self, other):
        if not isinstance(other, Poller):
            return False
        else:
            return all((super().__eq__(other),
                        self.config.series == other.config.series))

    def __ne__(self, other):
        return not self == other

    def run(self):
        """Perform one poll iteration.
        """
        # Get the current build configuration
        if not self.config.updated:
            logging.info("getting the build configuration from a changeset...")
            with self.repo.checkout(tempfile.mkdtemp()) as work:
                path = common.find_config(work.path)
                if path:
                    self.config.update(path)
                else:
                    logging.error("no build configuration found")

        # Poll for each series
        for series in self.config.series:

            branches, command, rebuild, start, sleep = self.config.get_poll(series, all_branches=self.repo.branches)

            now = int(time.time())
            remaining = (self.times[series] + sleep) - now
            if remaining > 0:
                logging.debug("series [{s}] will sleep for another {t} seconds...".format(s=series, t=remaining))
                time.sleep(settings.POLL_DELAY)
                continue
            self.times[series] = now

            logging.debug("determining if series [{0}] should run...".format(series))
            if self.call(command):

                logging.debug("polling for series [{0}]...".format(series))
                for branch in branches:
                    for changeset in self.repo.get_heads(branch):

                        request = rebuild
                        if not request:
                            logging.debug("checking if '{c}' ({b}) requires build...".format(c=changeset.rev, b=branch))
                            for build in self.repo.builds:
                                if build.changeset.rev == changeset.rev:
                                    logging.debug("already built: {0}".format(changeset.rev))
                                    break
                            else:
                                request = True
                        if request:
                            self.count += 1
                            logging.info("requesting builds of {0} in '{1}'...".format(changeset, changeset.repo))
                            for environment in self.config.environments:
                                name = self.name(self.count, now, series, environment, changeset, branch)
                                request = self.repo.request_build(name, series, environment,
                                                                  start, changeset.rev, branch=branch)
                                logging.info("new build request: {0}".format(request))
                            self.repo.push()

    def test(self):
        """Perform one poll iteration locally as a test.
        """
        for series in self.config.series:

            branches, command, rebuild, start, sleep = self.config.get_poll(series, all_branches=self.repo.branches)
            now = time.time()
            if now - self.times[series] > sleep:

                self.times[series] = now
                logging.debug("determining if series [{0}] should run...".format(series))
                if self.call(command):

                    for branch in branches:
                        for changeset in self.repo.get_heads(branch):

                            request = rebuild
                            if not request:
                                logging.info("checking if '{c}' ({b}) requires build...".format(c=changeset, b=branch))
                                for build in self.repo.builds:
                                    if build.changeset.rev == changeset.rev:
                                        logging.info("already built: {0}".format(changeset))
                                        break
                                else:
                                    request = True
                            if request:
                                logging.debug("build request would start at [{0}]".format(start))
                                self.name(self.count, now, series, '<TEST>', changeset, branch)
                                logging.info("(new) build request: {0}".format(changeset))

    @staticmethod
    def call(command):
        """Run a build command in the current directory.
        @param command: shell string
        @return: indicates command returned no error
        """
        if command:
            logging.debug("$ {0}".format(command))
            retcode = subprocess.call(command, shell=True)
        else:
            logging.debug("$ (no command)")
            retcode = 0
        logging.debug("return code: {0}".format(retcode))
        return retcode == 0

    @staticmethod
    def name(total, now, series, environment, changeset, branch):  # pylint: disable=R0913
        """Return a name for the next build.
        """
        timestamp = time.strftime("%m/%d %H:%M:%S", time.localtime(now))
        name = "{n} {c}".format(t=total, n=timestamp,
                                s=series, e=environment,
                                c=changeset, b=branch)
        logging.debug("new build name: {0}".format(name))
        return name


def run(config, daemon=False, test=False):
    """Run a poller for each repository.
    @param config: common Config object
    @param daemon: run as a daemon
    @param test: run locally as a test
    @return: indicates poller(s) ran successfully
    """
    pollers = [Poller(repo, config.copy()) for repo in config.repos]
    if not pollers:
        return False

    while True:
        for poller in pollers:
            if test:
                logging.info("testing {p}...".format(p=poller))
                poller.test()
            else:
                logging.log(logging.DEBUG if daemon else logging.INFO,
                            "running {p}...".format(p=poller))
                poller.run()
        if not daemon or test:
            break

    return True


# TODO: share the common logic with tracking, builder, and poller
def main():  # pragma: no cover, integration
    """Process command-line arguments and run the program.
    """
    # Main parser
    parser = argparse.ArgumentParser(prog=POLLER, description=__doc__,
                                     formatter_class=common.formatter_class)
    parser.add_argument('-V', '--version', action='version', version=VERSION)
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help="enable verbose logging")
    parser.add_argument('-d', '--daemon', action='store_true',
                        help="keep the process running")
    parser.add_argument('-t', '--test', action='store_true',
                        help="dry run locally as a test")
    parser.add_argument('repo', nargs='*', help="repository names")
    parser.add_argument('--config', metavar='PATH',
                        help="path to a configuration file")
    parser.add_argument('--no-config', action='store_true',
                        help="ignore local configuration files")

    # Parse arguments
    args = parser.parse_args()

    # Configure logging
    common.configure_logging(args.verbose)

    # Parse the configuration file
    config = common.parse_config(args.config, not args.no_config,
                                 parser.error, repos=args.repo)
    if not config.repos:
        parser.error("specify at least one repository")

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

if __name__ == '__main__':  # pragma: no cover, integration
    main()
