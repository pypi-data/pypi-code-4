import sys
import urllib2
from threading import Thread
from urllib import urlencode


LEVELS = ('debug', 'info', 'warning', 'error', 'critical')


def stuff(url, user, log, level, message, **kwargs):
    """
    Puts the data to remote location
    """
    data = kwargs
    data.update({
        'user': user,
        'log': log,
        'level': level,
        'message': message
    })
    for k, v in data.iteritems():
        if isinstance(data[k], unicode):
            data[k] = v.encode('utf-8')
    urllib2.urlopen(url, urlencode(data))


class BaseLogger(object):
    def debug(self, message, **kwargs):
        self.log('debug', message, **kwargs)

    def info(self, message, **kwargs):
        self.log('info', message, **kwargs)

    def warning(self, message, **kwargs):
        self.log('warning', message, **kwargs)

    def error(self, message, **kwargs):
        self.log('error', message, **kwargs)

    def critical(self, message, **kwargs):
        self.log('critical', message, **kwargs)


class Logger(BaseLogger):
    def __init__(self, url, user, log, min_level=None):
        self._url = url
        self._user = user
        self._log = log
        self._min_level_idx = min_level and LEVELS.index(min_level)

    def log(self, level, message, **kwargs):
        """
        Thread wrapper for stuff
        """
        try:
            idx = LEVELS.index(level)
        except ValueError:
            idx = None
        if self._min_level_idx == None or idx == None or idx >= self._min_level_idx:
            thread = Thread(
                target=stuff,
                args=(self._url, self._user, self._log, level, message),
                kwargs=kwargs
                )
            thread.start()


class ConsoleLogger(BaseLogger):
    def log(self, level, message, **kwargs):
        msg = '%s: %s' % (level, message)
        for k, v in kwargs.iteritems():
            msg += ', %s=%s' % (k, v)
        sys.stderr.write(msg + '\n')

