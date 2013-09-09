#coding:utf-8
import logging
import contextlib


logger = logging.getLogger(__name__)



class ConnectionPool(object):
    def __init__(self):
        self._pool = []

    @contextlib.contextmanager
    def _acquire_connection(self):
        broken_connections = []

        for connection in self._pool:
            if connection.broken:
                broken_connections.append(connection)
                continue
            if connection.lock.acquire(blocking=False):
                logger.debug("Reusing existing connection: %s", connection)
                break
        else:
            connection = self._create_connection()
            connection.lock.acquire(blocking=False)
            self._pool.append(connection)
            logger.debug("Creating new connection: %s", connection)

        for broken_connection in broken_connections:
            logger.debug("Cleaning up broken connection: %s")
            self._pool.remove(broken_connection)

        yield connection

        connection.lock.release()

    def _create_connection(self):
        raise NotImplementedError()
