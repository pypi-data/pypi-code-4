"""A simple logger initialization for command line tools."""

from __future__ import print_function

import logging
import sys


class _OutputHandler(logging.Handler):
    """
    Log handler that logs debug and info messages to stdout and all other
    messages to stderr.
    """

    def emit(self, record):
        self.acquire()

        try:
            stream = sys.stdout if record.levelno <= logging.INFO else sys.stderr
            print(self.format(record), file=stream)
        except:
            self.handleError(record)
        finally:
            self.release()


def setup(name=None, debug_mode=False, with_time=None, filter=None, level=None):
    """Initializes logging to stdout/stderr."""

    logging.addLevelName(logging.DEBUG,    "D")
    logging.addLevelName(logging.INFO,     "I")
    logging.addLevelName(logging.WARNING,  "W")
    logging.addLevelName(logging.ERROR,    "E")
    logging.addLevelName(logging.CRITICAL, "C")

    log = logging.getLogger() if name is None else logging.getLogger(name)

    if level is None:
        log.setLevel(logging.DEBUG if debug_mode else logging.INFO)
    else:
        log.setLevel(level)

    format = ""
    if with_time or debug_mode and with_time != False:
        format += "%(asctime)s.%(msecs)03d "
    if debug_mode:
        format += "(%(filename)12.12s:%(lineno)04d) [%(name)16.16s]: "
    format += "%(levelname)s: %(message)s"

    handler = _OutputHandler()
    handler.setFormatter(logging.Formatter(format, "%Y.%m.%d %H:%M:%S"))
    if filter is not None:
        handler.addFilter(filter)

    log.addHandler(handler)
