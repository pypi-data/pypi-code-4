""" It speeds up the socket connection """
import socket
import logging
from multiprocessing.connection import Client
from logging.handlers import DEFAULT_TCP_LOGGING_PORT


logger = logging.getLogger(__name__)


def coroutine(func):
    """ Decorator for the coroutine starting """
    def start(*args, **kwargs):
        g = func(*args, **kwargs)
        g.next()
        return g
    return start


def setupClient():
    """ It sets up the socket connection """
    try:
        conn = Client(('localhost', DEFAULT_TCP_LOGGING_PORT))
    except socket.error as e:
        logger.exception(e)
    else:
        return conn


class Sender(object):
    """ The class is dedicated to retaining the socket connection """
    conn = setupClient()

    @staticmethod
    @coroutine
    def sendData():
        """ Send data to application (e.g: daemon) """
        while(True):
            data = (yield)
            if not Sender.conn:
                Sender.conn = setupClient()
                logger.info(
                    "Can't send data."
                    "Please, check your socket (%s, %s)." %
                    ('localhost', DEFAULT_TCP_LOGGING_PORT)
                )
                continue
            try:
                Sender.conn.send(data)
            except IOError as e:
                logger.exception(e)
                Sender.conn = setupClient()
