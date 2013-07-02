#coding=utf8

"""Usage:
  ililac start
  ililac stop
  ililac restart
"""

from daemon import Daemon
from lilac.server import server
from lilac.cli import docopt
from lilac.logger import logger
import logging
import sys


class LilacDaemon(Daemon):

    def run(self):
        logger.setLevel(logging.ERROR)
        server.run(True, 8888)
        logger.setLevel(logging.INFO)


lilac_daemon = LilacDaemon("/tmp/lilac-daemon.pid", stdout="/dev/stdout")


def main():
    dct = docopt(__doc__)
    # set logger level to info
    logger.setLevel(logging.INFO)

    if dct["start"]:
        lilac_daemon.start()
    elif dct["stop"]:
        lilac_daemon.stop()
    elif dct["restart"]:
        lilac_daemon.restart()
    else:
        exit(__doc__)


if __name__ == '__main__':
    main()
