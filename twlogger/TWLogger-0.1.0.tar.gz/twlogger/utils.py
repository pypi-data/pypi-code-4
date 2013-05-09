"""Common utility functions."""

import sys
import traceback


def get_environ_dict(environ):
    """Build and return environment dictionary from request environ.

    :param environ: request environ dictionary

    """
    environment = {
        'REQUEST_METHOD': environ.get('REQUEST_METHOD'),
        'QUERY_STRING': environ.get('QUERY_STRING'),
        'SERVER_NAME': environ.get('SERVER_NAME'),
        'SERVER_PORT': environ.get('SERVER_PORT'),
        'REMOTE_ADDR': environ.get('REMOTE_ADDR'),
    }
    for key, value in environ.items():
        if (key.startswith('HTTP_') or
                key in ('CONTENT_TYPE', 'CONTENT_LENGTH')):
            environment[key] = value
    return environment


def build_exc_info(exc_info=None):
    """Process exception information for event message.

    Return 4-tuple ready for event data: message, place, exception type and
    traceback string.

    :param exc_info: information about exception.  If ``None`` (default),
        ``sys.exc_info()`` will be used.

    """
    if exc_info is None:
        exc_info = sys.exc_info()
    if not all(exc_info):
        raise ValueError('No exception found.')
    exc_type, exc_value, exc_tb = exc_info

    # Building exception message.
    message_list = traceback.format_exception_only(exc_type, exc_value)
    message = '\n'.join(message_list).strip('\n')

    # Building place string from traceback.
    filename, lineno, func, source = traceback.extract_tb(exc_tb)[-1]
    place = build_place_string(filename, lineno, func)
    place = 'File "%s", line %d, in %s' % (filename, lineno, func)

    # Formatting traceback.
    tb = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))

    return message, place, exc_type, tb


def build_place_string(filename, lineno, module):
    """Return place string for log event.

    Example::

        >>> build_place_string('/foo/bar.py', 71, 'foo_bar')
        'File "/foo/bar.py", line 71, in foo_bar'

    :param filename: name of the file
    :param lineno: line number
    :param module: name of module or function

    """
    place = 'File "%s", line %d, in %s' % (filename, lineno, module)
    return place
