"""Client for communication with TaskWorkshop."""

import os
import logging

import requests

from . import __version__, improved_json as json
from .utils import build_exc_info


logger = logging.getLogger('twlogger')
error_logger = logging.getLogger('twlogger.error')


class Client(object):

    """Client for communication with TaskWorkshop.

    Example usage::

        >>> client = Client()
        >>> client.log_event('info', 'Some info log',
        ...                  place='File: "/foo/bar.py", line: 71, in foo_bar')
        >>> try:
        ...     1 / 0
        ... except ZeroDivisionError:
        ...     client.capture_exception()

    :param url: TaskWorkshop exceptions log URL.  If none given, it will be
        read from ``TWLOGGER_URL`` environment variable.

    """

    def __init__(self, url=None):
        if url is None:
            url = os.environ.get('TWLOGGER_URL')
        if not url:
            raise ValueError('No URL given for TWLogger Client.')
        self.url = url

    def build_message(self, event_type, message, place=None, exc_class=None,
                      traceback=None, application_time=None, **environment):
        r"""Return event dictionary that can be dumped into JSON object.

        :param event_type: type of event, one of ``exception``, ``error``,
          ``warning``, ``info``
        :param message: event message
        :param place: exception or log place, e.g. file path and line number,
            defaults to ``None``
        :param exc_class: exception class name, e.g. ``ValueError``, defaults
            to ``None``
        :param traceback: exception traceback string, defaults to ``None``
        :param application_time: :py:class:`datetime.datetime` object, optional
            event time
        :param \*\*environment: extra environment dictionary.

        """
        details = {'message': message}
        if place:
            details['place'] = place
        if exc_class:
            details['class'] = exc_class
        if traceback:
            details['traceback'] = traceback

        event_dict = {
            'type': event_type,
            'client': {
                'name': 'TWLogger',
                'version': __version__,
            },
            'details': details,
            'language': 'Python',
            'environment': environment,
        }
        if application_time:
            event_dict['time'] = application_time

        return event_dict

    def encode_message(self, message):
        """Return given message serialized into a JSON object.

        Encode using :class:`twlogger.improved_json.ImprovedJSONEncoder`.

        :param message: event dictionary from :meth:`build_message`

        """
        return json.dumps(message)

    def send(self, message):
        """Encode message and send to TaskWorkshop server.

        On success return 2-tuple: events limit and number of remaining events,
        on error return ``None``.

        Log limits info to ``twlib`` logger and request error to
        ``twlib.error`` logger.

        :param message: event dictionary to be sent

        """
        data = self.encode_message(message)
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(self.url, data=data, headers=headers,
                                     verify=False)
        except requests.ConnectionError:
            error_logger.exception('Failed to send event.')
        else:
            if response.status_code == 200:
                body = response.json()
                message = 'Limit: %s, remaining: %s' % (
                    body['limit'], body['remaining'])
                logger.info(message)
                return body['limit'], body['remaining']
            else:
                self._log_response_error(response)

    def log_event(self, event_type, message, place=None, exc_class=None,
                  traceback=None, application_time=None, **environment):
        r"""Build event message and send it to TaskWorkshop server.

        On success return 2-tuple: events limit and number of remaining events,
        on error return ``None``.

        :param event_type: type of event, one of ``exception``, ``error``,
          ``warning``, ``info``
        :param message: event message
        :param place: event place, e.g. file path and line number, defaults
            to ``None``
        :param exc_class: exception class name, e.g. ``ValueError``, defaults
            to ``None``
        :param traceback: exception traceback string, defaults to ``None``
        :param application_time: :py:class:`datetime.datetime` object, optional
            event time.
        :param \*\*environment: extra environment dictionary.

        """
        data = self.build_message(
            event_type,
            message,
            place=place,
            exc_class=exc_class,
            traceback=traceback,
            application_time=application_time,
            **environment)
        return self.send(data)

    def capture_exception(self, exc_info=None, **environment):
        r"""Capture exception, build message and send it.

        On success return 2-tuple: events limit and number of remaining events,
        on error return ``None``.

        :param exc_info: 3-tuple information about exception.  If ``None``
            (default), ``sys.exc_info()`` will be used.
        :param \*\*environment: extra environment dictionary.

        """
        message, place, exc_type, tb = build_exc_info(exc_info)
        return self.log_event(
            'exception',
            message,
            place=place,
            exc_class=exc_type,
            traceback=tb,
            **environment)

    def _log_response_error(self, response):
        """Log error from TaskWorkshop API response.

        Use ``twlib.error`` logger.

        :param response: :class:`requests.Response` object

        """
        if response.status_code == 404:
            reason = ('either your project no longer exists or API key was '
                      'changed.')
        else:
            try:
                body = response.json()
                reason = body['error']
            except (ValueError, KeyError):
                reason = response.reason
        message = 'Got %d: %s' % (response.status_code, reason)
        error_logger.error(message)
