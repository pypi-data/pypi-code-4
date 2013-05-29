# -*- coding: utf-8 -*-


class AmqpRpcException(Exception):
    """Base class for amphora exceptions"""
    pass


class NoResult(AmqpRpcException):
    """Raises by :py:attr:`amphora.AmqpRpcClient.call`
    when request is timed out."""
    pass


class WrongRequest(AmqpRpcException):
    """Raises by :py:attr:`amphora.AmqpRpcClient.call`
    or by ``gevent.AsyncResult.get()`` returned by
    :py:attr:`amphora.AmqpRpcClient.defer` when server
    can't parse request. For example, when you try
    to call function not registered in server."""
    pass


class WrongResult(AmqpRpcException):
    """Raises by :py:attr:`amphora.AmqpRpcClient.call`
    or by ``gevent.AsyncResult.get()`` returned by
    :py:attr:`amphora.AmqpRpcClient.defer` when server
    can't parse response. Normally you will never get
    this exception."""
    pass


class RemoteException(AmqpRpcException):
    """Raises by :py:attr:`amphora.AmqpRpcClient.call`
    or by ``gevent.AsyncResult.get()`` returned by
    :py:attr:`amphora.AmqpRpcClient.defer` when remote
    function raises exception.

    :param error_type: Class name of remote exception.
    :type error_type: str
    :param args: Arguments passed to remote exception.
    :type args: tuple

    Example:

    .. code-block:: python

       # server.py
       @server.add_function
       def divide(x, y):
           if x < 0:
               raise ValueError('x', x)
           elif y < 0:
               raise ValueError('y', y)
           else:
               return x / y

       # client.py
       from amphora import RemoteException
       client.call.divide(6, 3)  # Prints "2"

       try:
          client.call.divide(-5, 5)
       except RemoteException as exc:
          print exc.error_type  # Prints "ValueError"
          print exc.args  # Prints '("x", -5)'

       try:
          client.call.divide(10, 0)
       except RemoteException as exc:
          print exc.error_type  # Prints "ZeroDivisionError"
    """
    def __init__(self, error_type, args):
        super(RemoteException, self).__init__(*args)
        self.error_type = error_type

    def __str__(self):
        return '{0}: {1}'.format(
            self.error_type, self.args[0] if self.args else '')


class IgnoreRequest(Exception):
    """Reject request when raised in :py:class:`~amphora.AmqpRpcServer`
    or ignore it when raised in :py:class:`~amphora.AmqpRpcFanoutServer`.
    """
    pass
