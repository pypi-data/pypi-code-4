#!/usr/bin/env python

"""
Common parsing and testing functions.
"""

import os
import sys
import shutil
import tempfile
import subprocess
import argparse
import logging
import ConfigParser
from collections import defaultdict

from veracity import TRACKING, POLLER, BUILDER
from veracity import settings

SGCLOSET = os.getenv('SGCLOSET')


class Config(object):
    """Stores poller and builder configuration settings."""

    REPOSITORIES = 'repositories'
    ENVIRONMENTS = 'environments'
    SERIES = 'series'

    ALL = '*'
    DEFAULT_QUEUED = 'Q'  # TODO: should this be a CLI option?

    BRANCHES = 'branches'
    SLEEP = 'sleep'
    START = 'start'

    ENTER = 'enter'
    PATH = 'path'
    COMMAND = 'command'
    FAIL = 'fail'
    EXIT = 'exit'

    def __init__(self, path=None, repos=None, series=None, envs=None):
        self.config = defaultdict(lambda: defaultdict(lambda: defaultdict(str)))
        if path:
            self.update(path)
        if repos:
            logging.debug("overriding repos in config...")
            self.config[TRACKING][Config.REPOSITORIES] = repos
        if series:
            logging.debug("overriding series in config...")
            self.config[TRACKING][Config.SERIES] = series
        if envs:
            logging.debug("overriding environments in config...")
            self.config[TRACKING][Config.ENVIRONMENTS] = envs
        self.updated = False

    def update(self, path):
        """Update the config from a config file.
        @param path: path to config file
        """
        logging.debug("parsing config {0}...".format(path))
        cfg = ConfigParser.RawConfigParser()
        cfg.read(path)
        section = TRACKING
        if cfg.has_section(section):
            for option, value in cfg.items(section):
                # TODO: is there a more elegant way to handle the override?
                if option == Config.REPOSITORIES:
                    if not self.config[section][Config.REPOSITORIES]:
                        self.config[section][Config.REPOSITORIES] = [r.strip() for r in value.split(',')]
                elif option == Config.ENVIRONMENTS:
                    if not self.config[section][Config.ENVIRONMENTS]:
                        self.config[section][Config.ENVIRONMENTS] = [r.strip() for r in value.split(',')]
                elif option == Config.SERIES:
                    if not self.config[section][Config.SERIES]:
                        self.config[section][Config.SERIES] = [r.strip() for r in value.split(',')]
                else:
                    logging.debug("unknown option in section [{s}]: {o}".format(s=section, o=option))

        for section in (POLLER, BUILDER):
            if cfg.has_section(section):
                for option, value in cfg.items(section):
                    alias, setting = option.split('_')
                    self.config[section][alias.upper()][setting] = value  # TODO: is upper required?
        self.display()
        self.updated = True

    def display(self):
        """Write the current configuration to the log.
        """
        for section, options in self.config.iteritems():
            for option, values in options.iteritems():
                if section == TRACKING:
                    logging.debug("config[{s}][{o}] = {v}".format(s=section, o=option, v=values))
                else:
                    for name, value in values.iteritems():
                        logging.debug("config[{s}][{o}][{n}] = {v}".format(s=section, o=option, n=name, v=value))

    @property
    def repos(self):
        """Get the list of repository names.
        """
        return self.config[TRACKING][Config.REPOSITORIES]

    @property
    def series(self):
        """Get the list of series aliases.
        """
        return self.config[TRACKING][Config.SERIES]

    @property
    def environments(self):
        """Get the list of environment aliases.
        """
        return self.config[TRACKING][Config.ENVIRONMENTS]

    @property
    def starts(self):
        """Get a list of initial state aliases.
        """
        return [alias for alias in self.enters if alias not in self.exits] or [Config.DEFAULT_QUEUED]

    @property
    def ends(self):
        """Get a list of final state aliases.
        """
        return [alias for alias in self.exits if alias not in self.enters]

    @property
    def enters(self):
        """Get a list of entry state aliases.
        """
        aliases = []
        for data in self.config[BUILDER].itervalues():
            for setting, value in data.iteritems():
                if setting == Config.ENTER:
                    aliases.append(value)
        return aliases

    @property
    def exits(self):
        """Get a list of exit and fail (terminal) state aliases.
        """
        aliases = []
        for data in self.config[BUILDER].itervalues():
            for setting, value in data.iteritems():
                if setting in (Config.FAIL, Config.EXIT):
                    aliases.append(value)
        return aliases

    @property
    def fails(self):
        """Get a list of fail state aliases.
        """
        aliases = []
        for data in self.config[BUILDER].itervalues():
            for setting, value in data.iteritems():
                if setting == Config.FAIL:
                    aliases.append(value)
        return aliases

    def enter(self, status):
        """Get the next build state alias.
        @param status: current state alias
        @return: next state alias
        """
        logging.debug("entering next state from [{0}]...".format(status))
        for alias, data in self.config[BUILDER].iteritems():
            if data[Config.ENTER] == status:
                break
        else:
            logging.debug("no next state found, staying...")
            alias = status
        logging.info("entered build state: [{0}]".format(alias))
        return alias

    def fail(self, status):
        """Get the build state alias for a failure.
        @param status: current state alias
        @return: failed state alias
        """
        logging.debug("failing from build state [{0}]...".format(status))
        alias = self.config[BUILDER][status][Config.FAIL]
        logging.info("entered build state: [{0}]".format(alias))
        return alias

    def exit(self, status):
        """Get the build state alias for success.
        @param status: current state alias
        @return: passed state alias
        """
        logging.debug("exiting from build state [{0}]...".format(status))
        alias = self.config[BUILDER][status][Config.EXIT]
        logging.info("entered build state: [{0}]".format(alias))
        return alias

    def get_poll(self, series, all_branches=None):
        """Get the items to perform a poll operation.
        @param series: series alias
        @param all_branches: list of branches to match against
        @return: branches, command, start, sleep
        """
        logging.debug("getting poll operations for series [{0}]...".format(series))
        all_branches = all_branches or []
        branches = []
        for name in (b.strip() for b in self.config[POLLER][series][Config.BRANCHES].split(',')):
            if name.startswith(Config.ALL) or name.endswith(Config.ALL):
                logging.debug("branch pattern: {0}".format(name))
                label = name.strip('*')
                for name2 in (str(b) for b in all_branches):
                    if name2.startswith(label) or name2.endswith(label):
                        logging.debug("matched branch: {0}".format(name2))
                        branches.append(name2)
            else:
                branches.append(name)
        command = self.config[POLLER][series][Config.COMMAND]
        start = self.config[POLLER][series][Config.START]
        try:
            sleep = eval(self.config[POLLER][series][Config.SLEEP])  # TODO: this parsing should happen sooner
        except SyntaxError:
            sleep = 0
        return branches, command, start, sleep

    def get_build(self, status):  # pragma: no cover - different coverage by OS
        """Get the items to perform a build operation.
        @param status: current state alias
        @return: path, command
        """
        logging.debug("getting build operations for state [{0}]...".format(status))
        path = self.config[BUILDER][status][Config.PATH]
        if os.name == 'nt' and (Config.COMMAND + '-nt') in self.config[BUILDER][status]:
            command = self.config[BUILDER][status][Config.COMMAND + '-nt']
        else:
            command = self.config[BUILDER][status][Config.COMMAND]
        return path, command


formatter_class = lambda prog: argparse.HelpFormatter(prog, max_help_position=32)  # pylint: disable=C0103


def configure_logging(verbosity=0):  # pragma: no cover - tested manually
    """Configure logging using the provided verbosity level (0+)."""

    class WarningFormatter(logging.Formatter, object):
        """Always displays the verbose logging format for warnings or higher."""

        def __init__(self, default_format, verbose_format, *args, **kwargs):
            super(WarningFormatter, self).__init__(*args, **kwargs)
            self.default_format = default_format
            self.verbose_format = verbose_format

        def format(self, record):
            if record.levelno > logging.INFO or logging.root.getEffectiveLevel() < logging.INFO:
                self._fmt = self.verbose_format
            else:
                self._fmt = self.default_format
            return super(WarningFormatter, self).format(record)

    # Configure the logging level and format
    if verbosity >= 1:
        level = settings.VERBOSE_LOGGING_LEVEL
        if verbosity >= 3:
            default_format = verbose_format = settings.VERBOSE3_LOGGING_FORMAT
        elif verbosity >= 2:
            default_format = verbose_format = settings.VERBOSE2_LOGGING_FORMAT
        else:
            default_format = verbose_format = settings.VERBOSE_LOGGING_FORMAT
    else:
        level = settings.DEFAULT_LOGGING_LEVEL
        default_format = settings.DEFAULT_LOGGING_FORMAT
        verbose_format = settings.VERBOSE_LOGGING_FORMAT

    # Set a custom formatter
    logging.basicConfig(level=level)
    logging.root.handlers[0].setFormatter(WarningFormatter(default_format, verbose_format))


def check_user(daemon, error):  # pragma: no cover - tested manually
    """Confirm that a root user specified a custom closet and is a daemon.
    @param daemon: indicates program is being run as a daemon
    @param error: function to call on error
    """
    if os.name != 'nt' and os.geteuid() == 0:  # pylint: disable=E1101
        if daemon and SGCLOSET:
            logging.info("running daemon as root, SGCLOST={0}".format(SGCLOSET))
        else:
            error("root user must set SGCLOSET and run as a daemon")


def parse_config(path, error, repos=None, series=None, envs=None):
    """Parse the config file.
    @param error: function to call on error
    @param repos: overriding list of repository names
    @param series: overriding list of series aliases
    @param envs: overriding list of environment aliases
    @return: Config object
    """
    config = Config(repos=repos, series=series, envs=envs)

    path = path or find_config(os.getcwd())
    if path:
        if os.path.isfile(path):
            config.update(path)
        else:
            error("config file does not exist: {0}".format(path))

    return config


def find_config(cwd):
    """Find the first available configuration file.
    @param cwd: current working directory
    @return: path or None
    """
    for directory in (cwd, os.path.expanduser("~")):
        for filename in ('setup.cfg', '.veracity'):
            path = os.path.join(directory, filename)
            if os.path.isfile(path):
                logging.debug("found config: {0}".format(path))
                return path


def create_test_repo(name):  # pragma: no cover - not used every test iteration
    """Creates a test repository for integration tests.
    """
    sys.stderr.write('\n' + "Creating a test repository for integration tests..." + '\n\n')
    # Initialize a new repository
    subprocess.call(['vv', 'repo', 'new', name])
    subprocess.call(['vv', 'config', 'set', '/instance/{0}/paths/default'.format(name), name])
    # Check out to a temporary location
    temp = tempfile.mkdtemp()
    os.chdir(temp)
    subprocess.call(['vv', 'checkout', name])
    # Commit 1
    with open("foo.h", 'w') as new:
        new.write("this is foo.h")
    with open("bar.c", 'w') as new:
        new.write("this is ")
    subprocess.call(['vv', 'addremove'])
    subprocess.call(['vv', 'whoami', '--create', 'testuser'])
    subprocess.call(['vv', 'commit', '--message', "added sample files"])
    # Commit 2
    with open("bar.c", 'a') as new:
        new.write("bar.c ")
    subprocess.call(['vv', 'commit', '--message', "added missing text"])
    # Initialize build configuration
    os.chdir(os.path.dirname(__file__))
    subprocess.call([sys.executable, 'vscript.py', name])
    # Cleanup
    shutil.rmtree(temp)
    sys.stderr.write('\n')


def delete_test_repo(name):  # pragma: no cover - not used every test iteration
    """Delete the test repository.
    """
    sys.stderr.write('\n' + "Deleting the test repository..." + '\n\n')
    subprocess.call(['vv', 'repo', 'delete', name])
