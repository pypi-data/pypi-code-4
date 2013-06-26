"""Logging utilities (for sessions and experiment logs)."""

# Author: Salvatore Masecchia <salvatore.masecchia@disi.unige.it>,
#         Grzegorz Zycinski <grzegorz.zycinski@disi.unige.it>
# License: new BSD.

import logging
import logging.handlers
import socket

LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

class PPlusLogger(object):
    def __init__(self, name, path, level):
        """PPlus File Logger.

        This class is used to manage sessions and experiment logs.
        The only responsibility of this class is to properly format log
        messages. Through the :attr:`PPlusConnection.session_logger` attribute
        of a :class:`pplus.PPlusConnection` instance, client code can add
        messages into the current session log.

        Parameters
        ----------
        name : str
            log *hierarchical* name. PPlus names all the log with a root prefix
            'pplus'. A session log will have name 'pplus.<session_id>'
        path : str
            log file path
        level : str, [ 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL' ]
            sets the log level

        """
        self._logger = logging.getLogger(name)
        self._handler = logging.FileHandler(filename=path, mode='w',
                                            delay=True)

        formatter = logging.Formatter("%(asctime)s - %(name)s - " +
                                      socket.gethostname() +
                                      " - %(levelname)s - %(message)s")
        self._handler.setFormatter(formatter)
        self._logger.addHandler(self._handler)

        self._logger.setLevel(LOG_LEVELS[level.upper()])

    def __getattr__(self, attr):
        return getattr(self._logger, attr)
