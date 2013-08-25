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

try:  # pragma: no cover - OS determines path coverage
    if os.name == 'nt':
        import pbs  # pylint: disable=F0401,W0611
        from pbs import ErrorReturnCode  # pylint: disable=F0401,W0611
        if not os.path.isfile(settings.VSCRIPT_PATH_WINDOWS):
            raise ImportError
        vscript = pbs.Command(settings.VSCRIPT_PATH_WINDOWS)  # pylint: disable=C0103
    else:
        from sh import ErrorReturnCode  # pylint: disable=F0401,W0611
        from sh import vscript  # pylint: disable=F0401,E0611
except ImportError:  # pragma: no cover - only occurs with missing dependency
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
        if "is not a valid" in msg:  # pragma: no cover, TODO: try to get coverage
            raise ValueError("invalid arguments to report build: {0}".format(' '.join(args)))
        elif "statusRec is null" in msg:
            raise VeracityScriptException("no build configuration for: {0}".format(repo))
        elif "is null" in msg:
            logging.warning("no build defined for the current environment")
        else:
            raise


def run(*args, **kwargs):
    """Run a Veracity script with the given arguments.
    @raise VeracityScriptException: when Veracity scripting returns an error
    """
    command = vscript.bake(*args, **kwargs)
    logging.debug('$ ' + str(command))
    try:
        result = command()
    except ErrorReturnCode as erc:
        msg = ("\n\nIN: {0}"
               "\n\nRAN: {1}"
               "\n\nOUTPUT:{2}\n").format(os.getcwd(), erc.full_cmd,
                                          (erc.stdout or erc.stderr).strip())
        raise VeracityScriptException(msg)
    else:
        return result.stdout.strip()


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


if __name__ == '__main__':  # pragma: no cover - this is tested manually
    common.configure_logging()
    for name in sys.argv[1:]:
        print(init_builds(name))
