"""Logging handler for sending logs to TaskWorkshop."""

import logging

from .client import Client
from .utils import build_place_string


error_logger = logging.getLogger('twlogger.error')

#: List of :py:class:`logging.LogRecord` attributes which shouldn't be
#: submitted as extra environment variables in logs.
RECORD_ATTRIBUTES = (
    'args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename',
    'funcName', 'getMessage', 'levelname', 'levelno', 'lineno', 'message',
    'module', 'msecs', 'msg', 'name', 'pathname', 'process', 'processName',
    'relativeCreated', 'stack_info', 'thread', 'threadName',
)


class TWLoggerHandler(logging.Handler, object):

    """A logging handler for sending logs to TaskWorkshop.

    :param url: TaskWorkshop exceptions log URL.  If none given, it will be
        read from ``TWLOGGER_URL`` environment variable.
    :param level: log level.  Defaults to :py:data:`logging.NOTSET`, which
        causes all messages to be processed.
    :param client: :class:`twlogger.client.Client` object, optional

    """

    def __init__(self, url=None, level=logging.NOTSET, client=None):
        self.client = client or Client(url)
        super(TWLoggerHandler, self).__init__(level=level)

    def emit(self, record):
        """Send log to TaskWorkshop.

        If record has ``exc_info``, send ``exception`` event, otherwise define
        event type based on log level.

        Add extra record's attributes, process and thread info to event's
        environment.

        :param record: :py:class:`logging.LogRecord` object

        """
        try:
            self._emit(record)
        except Exception:
            try:
                self.client.capture_exception()
            except Exception:
                error_logger.exception('Failed to send handler error.')

    def _get_environment(self, record):
        """Return extra environment dictionary for log record."""
        environment = {
            'Args': record.args,
            'Logger name': record.name,
            'Function name': record.funcName,
            'Process': record.process,
            'Process name': record.processName,
            'Thread': record.thread,
            'Thread name': record.threadName,
        }
        for key, value in vars(record).items():
            if not key in RECORD_ATTRIBUTES and not key.startswith('_'):
                environment[key] = value
        return environment

    def _get_event_type(self, record):
        """Return event type based on log level."""
        if record.levelname == 'ERROR':
            event_type = 'error'
        elif record.levelname == 'WARNING':
            event_type = 'warning'
        else:
            event_type = 'info'
        return event_type

    def _get_place(self, record):
        """Return place string: file name, line number and module name."""
        place = build_place_string(
            record.filename,
            record.lineno,
            record.module)
        return place

    def _emit(self, record):
        """Capture exception or simple log and send event to TaskWorkshop."""
        environment = self._get_environment(record)
        if record.exc_info and all(record.exc_info):
            self.client.capture_exception(record.exc_info, **environment)
        else:
            event_type = self._get_event_type(record)
            place = self._get_place(record)
            self.client.log_event(
                event_type,
                record.getMessage(),
                place=place,
                **environment)
