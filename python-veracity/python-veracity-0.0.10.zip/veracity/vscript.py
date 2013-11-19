#!/usr/bin/env python

"""
Wrapper for Veracity's scripting interface.

To initialize a repository with a default build configuration::

    python vscript.py <REPO>

"""

import os
import sys
import json
import logging

from veracity import common
from veracity import settings

try:  # pragma: no cover, installation
    if os.name == 'nt':
        import pbs  # pylint: disable=F0401,W0611
        ErrorReturnCode = pbs.ErrorReturnCode
        if not os.path.isfile(settings.VSCRIPT_PATH_WINDOWS):
            raise ImportError
        vscript = pbs.Command(settings.VSCRIPT_PATH_WINDOWS)  # pylint: disable=C0103
    else:
        from sh import ErrorReturnCode  # pylint: disable=F0401,W0611
        from sh import vscript  # pylint: disable=F0401,E0611
except ImportError:  # pragma: no cover, installation
    raise EnvironmentError("vscript is not installed")


SCRIPT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files')
INIT_BUILDS_JS = 'init_builds.js'
REPORT_BUILD_JS = 'report_build.js'


class VeracityScriptException(Exception):
    """Exception for Veracity scripting errors."""
    pass


def init_builds(repo):
    """Run the script to initialize builds for a repository.
    @param repo: name of repository
    @return: output from script
    """
    os.chdir(SCRIPT_DIR)
    return run(INIT_BUILDS_JS, repo)


def report_build(repo, *args):
    """Run the script to report builds for a repository.
    @param repo: name of repository
    @param args: additional arguments
    @return: output from script
    """
    os.chdir(SCRIPT_DIR)
    try:
        return run(REPORT_BUILD_JS, repo, *args)
    except VeracityScriptException as exception:
        msg = str(exception).rsplit(':', 1)[-1].strip()
        logging.debug("{0} error: {1}".format(REPORT_BUILD_JS, msg))
        if "is not a valid" in msg:
            err = "invalid report build arguments: {0}".format(' '.join(args))
            raise ValueError(err)
        elif "statusRec is null" in msg:
            err = "no build configuration for: {0}".format(repo)
            raise VeracityScriptException(err)
        elif "is null" in msg:
            logging.warning("no build defined for the current environment")
        else:
            raise


def run(*args, **kwargs):
    """Run a Veracity script with the given arguments.
    @raise VeracityScriptException: when Veracity scripting returns an error
    """
    command = vscript.bake(*args, **kwargs)
    # TODO: this isn't working in Python 3
    # logging.debug("$ {0}".format(command))
    try:
        result = command()
    except ErrorReturnCode as erc:
        out = (erc.stdout or erc.stderr).decode('utf-8').strip()
        msg = ("\n\nIN: {0}"
               "\n\nRAN: {1}"
               "\n\nOUTPUT:{2}\n").format(os.getcwd(), erc.full_cmd, out)
        raise VeracityScriptException(msg)
    else:
        if os.name == 'nt':
            return result.stdout.strip()
        else:
            return result.stdout.decode('utf-8').strip()


def parse(output, style=None):
    """Yield parsed lines of Veracity scripting output.
    """
    if style == 'builds':

        data = json.loads(output) if output else []

        if 'builds' in data:
            for record in data['builds']:
                yield (record['recid'],
                       record['csid'],
                       record['name'],
                       record['series'],
                       record['environment'])
        elif 'build' in data:
            record = data['build']
            yield (record['recid'],
                   record['csid'],
                   record['name'],
                   record['series'],
                   record['environment'])
        else:
            logging.debug("no build data: {0}".format(repr(data)))

    else:
        raise ValueError("unknown style: {0}".format(style))


if __name__ == '__main__':  # pragma: no cover, integration
    common.configure_logging()
    for name in sys.argv[1:]:
        print((init_builds(name)))
