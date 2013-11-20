import sys
import logging
import datetime as dt

CRITICAL = logging.CRITICAL
FATAL = logging.FATAL
ERROR = logging.ERROR
WARNING = logging.WARNING
WARN = logging.WARN
INFO = logging.INFO
DEBUG = logging.DEBUG
NOTSET = logging.NOTSET

logcolors = {
    CRITICAL: '31',  # critical/fatal
    ERROR:    '31;01',
    WARNING:  '33',
    WARN:     '33',
    INFO:     '32',
    DEBUG:    '35',
    NOTSET:    '0'
}

logcolorsextralen = {
    CRITICAL: 10,  # critical/fatal
    ERROR:    13,
    WARNING:  10,
    WARN:     10,
    INFO:     10,
    DEBUG:    10,
    NOTSET:    9
}


logbase = {
    CRITICAL: 'CRITICAL',  # critical/fatal
    ERROR:    'ERROR',
    WARNING:  'WARNING',
    WARN:     'WARN',
    INFO:     'INFO',
    DEBUG:    'DEBUG',
    NOTSET:   'BLANK'
}

mycolors = {k: "\x1b[%sm|%9s | \x1b[00m" % (logcolors[k], v)
            for k, v in logbase.items()}
mycolorscontline = {k: "\x1b[%sm| \x1b[00m" % v
                    for k, v in logcolors.items()}
nocolors = {k: "|%9s | " % (v) for k, v in logbase.items()}


class PercentStyle(object):

    default_format = '%(message)s'
    asctime_format = '%(asctime)s'
    asctime_search = '%(asctime)'

    def __init__(self, fmt):
        self._fmt = fmt or self.default_format

    def usesTime(self):
        return self._fmt.find(self.asctime_search) >= 0

    def format(self, record):
        return self._fmt % record.__dict__


class Formatter(logging.Formatter):
    # converter = dt.datetime.utcfromtimestamp
    converter = dt.datetime.fromtimestamp

    def __init__(self, *args, **kwargs):
        self.pre = kwargs.pop('pre', mycolors)

        # due to ansi escape sequences (len() returns differnt length if
        # string contains escape sequences)
        self.lenstrip = kwargs.pop('lenstrip', logcolorsextralen)

        # custom continuation line
        self.contline = kwargs.pop('contline', mycolorscontline)

        super(Formatter, self).__init__(*args, **kwargs)
        self.datefmt = '%d %b %Y %H:%M:%S.%f'

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        s = ct.strftime(datefmt)[:-3]  # only show milliseconds
        return s

    def format(self, record):
        self._fmt = "%(asctime)s " + \
                    self.pre[record.levelno] + \
                    "%(message)s"
        if sys.version_info[0] > 2:
            self._style = PercentStyle(self._fmt)
            self._fmt = self._style._fmt
        logstr = logging.Formatter.format(self, record)
        # see http://www.velocityreviews.com/forums/t737197-re-python-logging-handling-multiline-log-entries.html
        # and see also
        # http://stackoverflow.com/questions/2186919/getting-correct-string-length-in-python-for-strings-with-ansi-color-codes
        try:
            header, _ = logstr.split(record.message)
            hlen = len(header) - 2  # -2 strips the last to chars needed to
                                  # add "| "
            if self.lenstrip is not None:
                hlen -= self.lenstrip[record.levelno]
            contline = '| ' if self.contline is None else \
                       self.contline[record.levelno]
            logstr = logstr.replace('\n', '\n' + ' ' * hlen + contline)
        except:
            pass
        return logstr
