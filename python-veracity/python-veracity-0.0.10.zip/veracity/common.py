#!/usr/bin/env python

"""
Common parsing and testing functions.
"""

import os
import copy
import argparse
import logging
import configparser
from collections import defaultdict

from veracity import TRACKING, POLLER, BUILDER
from veracity import settings

SGCLOSET = os.getenv('SGCLOSET')


class Config(object):
    """Stores poller and builder configuration settings."""

    FILENAMES = ('setup.cfg', '.veracity')

    REPOSITORIES = 'repositories'
    ENVIRONMENTS = 'environments'
    SERIES = 'series'

    ALL = '*'
    DEFAULT_QUEUED = 'Q'  # TODO: should this be a CLI option?

    BRANCHES = 'branches'
    REBUILD = 'rebuild'
    START = 'start'
    SLEEP = 'sleep'

    VIRTUALENV = 'virtualenv'
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

    def copy(self):
        """Return a new copy of the conifiguration.
        @return: new Config
        """
        config = Config()
        config.config = copy.deepcopy(self.config)
        config.updated = copy.copy(self.updated)
        return config

    def update(self, path):
        """Update the config from a config file.
        @param path: path to config file
        """
        logging.debug("parsing config {0}...".format(path))
        cfg = configparser.RawConfigParser()
        cfg.optionxform = str  # preserve case in options
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
                elif option == Config.VIRTUALENV:
                    self.config[section][Config.VIRTUALENV] = value.strip()
                else:
                    logging.debug("unknown option in section [{s}]: {o}".format(s=section, o=option))

        for section in (POLLER, BUILDER):
            if cfg.has_section(section):
                for option, value in cfg.items(section):
                    alias, setting = option.split('_')
                    self.config[section][alias][setting] = value
        self.display()
        self.updated = True

    def display(self):
        """Write the current configuration to the log.
        """
        for section, options in self.config.items():
            for option, values in options.items():
                if section == TRACKING:
                    logging.debug("config[{s}][{o}] = {v}".format(s=section, o=option, v=values))
                else:
                    for name, value in values.items():
                        logging.debug("config[{s}][{o}][{n}] = {v}".format(s=section, o=option, n=name, v=value))

    @property
    def repos(self):
        """Get the list of repository names.
        """
        return sorted(self.config[TRACKING][Config.REPOSITORIES])

    @property
    def series(self):
        """Get the list of series aliases.
        """
        return sorted(self.config[TRACKING][Config.SERIES])

    @property
    def environments(self):
        """Get the list of environment aliases.
        """
        return sorted(self.config[TRACKING][Config.ENVIRONMENTS])

    @property
    def virtualenv(self):
        """Get the name of virtualenv to create.
        """
        return self.config[TRACKING][Config.VIRTUALENV] or None

    @property
    def enters(self):
        """Get a list of entry status aliases.
        """
        aliases = []
        for data in self.config[BUILDER].values():
            for setting, value in data.items():
                if setting == Config.ENTER and value:
                    aliases.append(value)
        return sorted(aliases)

    @property
    def exits(self):
        """Get a list of exit and fail status aliases.
        """
        aliases = []
        for data in self.config[BUILDER].values():
            for setting, value in data.items():
                if setting in (Config.FAIL, Config.EXIT) and value:
                    aliases.append(value)
        return sorted(aliases)

    @property
    def fails(self):
        """Get a list of fail status aliases.
        """
        aliases = []
        for data in self.config[BUILDER].values():
            for setting, value in data.items():
                if setting == Config.FAIL and value:
                    aliases.append(value)
        return sorted(aliases)

    @property
    def starts(self):
        """Get a list of all initial status aliases.
        """
        aliases = ([alias for alias in self.enters
                    if alias not in (list(self.config[BUILDER].keys()) + self.exits)] or
                   [Config.DEFAULT_QUEUED])

        return sorted(aliases)

    @property
    def ends(self):
        """Get a list of all final status aliases.
        """
        aliases = [alias for alias in self.exits if alias not in self.enters]
        return sorted(aliases)

    def next(self, status):
        """Get the next build status alias.
        @param status: current status alias
        @return: next status alias
        """
        logging.debug("entering next state from [{0}]...".format(status))
        for alias, data in self.config[BUILDER].items():
            if data[Config.ENTER] == status:
                logging.info("entered build state: [{0}]".format(alias))
                return alias
        raise ValueError("no state to enter from [{0}]".format(status))

    def fail(self, status):
        """Get the build status alias for a failure.
        @param status: current status alias
        @return: failed status alias
        """
        logging.debug("failing from build state [{0}]...".format(status))
        alias = self.config[BUILDER][status][Config.FAIL]
        if alias:
            logging.info("entered build state: [{0}]".format(alias))
            return alias
        else:
            raise ValueError("no state to fail from [{0}]".format(status))

    def exit(self, status):
        """Get the build status alias for success.
        @param status: current status alias
        @return: passed status alias
        """
        logging.debug("exiting from build state [{0}]...".format(status))
        alias = self.config[BUILDER][status][Config.EXIT]
        if alias:
            logging.info("entered build state: [{0}]".format(alias))
            return alias
        else:
            return status

    def get_poll(self, series, all_branches=None):
        """Get the items to perform a poll operation.
        @param series: series alias
        @param all_branches: list of branches to match against
        @return: branches, command, rebuild, start, sleep
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
        command = self._get_command(self.config[POLLER][series])
        rebuild = self.config[POLLER][series][Config.REBUILD]
        start = self.config[POLLER][series][Config.START]
        try:
            sleep = eval(self.config[POLLER][series][Config.SLEEP])  # TODO: this parsing should happen sooner
        except SyntaxError:
            sleep = 0
        return branches, command, rebuild, start, sleep

    def get_build(self, status):
        """Get the items to perform a build operation.
        @param status: current status alias
        @return: path, command
        """
        logging.debug("getting build operations for state [{0}]...".format(status))
        path = self.config[BUILDER][status][Config.PATH]
        command = self._get_command(self.config[BUILDER][status])
        return path, command

    @staticmethod
    def _get_command(data):
        """Get an OS-specific command to run."""
        if os.name == 'nt' and (Config.COMMAND + '-nt') in data:
            return data[Config.COMMAND + '-nt']
        else:
            return data[Config.COMMAND]


formatter_class = lambda prog: argparse.HelpFormatter(prog, max_help_position=32)  # pylint: disable=C0103


def configure_logging(verbosity=0):
    """Configure logging using the provided verbosity level (0+)."""

    class WarningFormatter(logging.Formatter, object):  # pragma: no cover, manual test
        """Always displays the verbose logging format for warnings or higher."""

        def __init__(self, default_format, verbose_format, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.default_format = default_format
            self.verbose_format = verbose_format

        def format(self, record):
            if record.levelno > logging.INFO or logging.root.getEffectiveLevel() < logging.INFO:
                self._fmt = self.verbose_format
            else:
                self._fmt = self.default_format
            return super().format(record)

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


def check_user(daemon, error):  # pragma: no cover, TODO: does this need to be tested?
    """Confirm that a root user specified a custom closet and is a daemon.
    @param daemon: indicates program is being run as a daemon
    @param error: function to call on error
    """
    if os.name != 'nt' and os.geteuid() == 0:  # pylint: disable=E1101
        if daemon and SGCLOSET:
            logging.info("running daemon as root, SGCLOST={0}".format(SGCLOSET))
        else:
            error("root user must set SGCLOSET and run as a daemon")


def parse_config(path, find, error, walk=False, repos=None, series=None, envs=None):
    """Parse the config file.
    @param path: optional path to a configuration file
    @param find: look for a configuration file if one was not specified
    @param error: function to call on error
    @param walk: search recursively for a config
    @param repos: overriding list of repository names
    @param series: overriding list of series aliases
    @param envs: overriding list of environment aliases
    @return: Config object
    """
    config = Config(repos=repos, series=series, envs=envs)

    if not path and find:
        path = find_config(os.getcwd(), walk=walk)
    if path:
        if os.path.isfile(path):
            config.update(path)
        else:
            error("config file does not exist: {0}".format(path))

    return config


def find_config(cwd, walk=False):
    """Find the first available configuration file.
    @param cwd: current working directory
    @param walk: search recursively for a config
    @return: path or None
    """
    for dirpath in (items[0] for items in os.walk(cwd)):
        logging.debug(dirpath)
        for filename in ('setup.cfg', '.veracity'):
            path = os.path.join(dirpath, filename)
            if os.path.isfile(path):
                logging.debug("found config: {0}".format(path))
                return path
        if not walk:
            return None
