from __future__ import absolute_import

from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL
import logging
import logging.handlers
import sys


__all__ = [
    'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL',
]


class LevelColoringFormatter(logging.Formatter):
    GRAY, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

    LEVELS_TO_COLORS = {
        10: BLUE,
        20: GREEN,
        30: YELLOW,
        40: RED,
        50: RED,
    }

    def __init__(self, level, message):
        self.level_fmt = logging.Formatter(level)
        self.level_fmt.formatException = lambda *_: ''
        super(LevelColoringFormatter, self).__init__(message)

    def formatException(self, *args):
        exc = super(LevelColoringFormatter, self).formatException(*args)
        return ('-- start traceback ' + '-' * 50 + '\n'
                + exc + '\n'
                + '-- end traceback --' + '-' * 50)

    def hilite(self, string, color=None, bold=False, background=None):
        attr = []

        if color:
            attr.append(str(color + 30))

        if background:
            attr.append(str(background + 40))

        if bold:
            attr.append('1')

        return '\x1b[{0}m{1}\x1b[0m'.format(';'.join(attr), string)

    def format(self, record):
        l = self.level_fmt.format(record)
        ll = len(l)
        r = super(LevelColoringFormatter, self).format(record)
        r = r.splitlines()

        level = max(0, record.levelno)
        level = min(CRITICAL, level)
        level = level // 10 * 10

        color = LevelColoringFormatter.LEVELS_TO_COLORS[level]
        l = l.replace(record.levelname, self.hilite(record.levelname.lower(),
                                                    color=color), 1)

        s = l + r[0]
        if r:
            if len(r) == 1:
                return s
            else:
                return s + '\n' + '\n'.join((' ' * ll + r for r in r[1:]))


class StdioOnnaStick(object):
    """
    A class that pretends to be a file object and instead executes a callback
    for each line written to it.
    """

    softspace = 0
    mode = 'wb'
    name = '<stdio (log)>'
    closed = 0

    def __init__(self, callback):
        self.buf = ''
        self.callback = callback

    def close(self):
        pass

    def fileno(self):
        return -1

    def flush(self):
        pass

    def read(self):
        raise IOError("can't read from the log!")

    readline = read
    readlines = read
    seek = read
    tell = read

    def write(self, data):
        d = (self.buf + data).split('\n')
        self.buf = d[-1]
        messages = d[0:-1]
        for message in messages:
            self.callback(message)

    def writelines(self, lines):
        self.write('\n'.join(lines))


class PrintTo(object):
    def __init__(self, fh):
        self.fh = fh

    def __enter__(self):
        self.old = sys.stdout
        sys.stdout = self.fh

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self.old


class LevelDependentFormatter(logging.Formatter):
    def __init__(self, formats, default='%(message)'):
        self.formatters = {k: logging.Formatter(v) for k, v in
                           formats.iteritems()}
        self.default_formatter = logging.Formatter(default)

    def get_formatter(self, record):
        try:
            return self.formatters[record.levelno]
        except KeyError:
            return self.default_formatter

    def format(self, record):
        formatter = self.get_formatter(record)
        message = record.getMessage()
        s = []

        for line in message.splitlines():
            rec = logging.LogRecord(
                record.name,
                record.levelno,
                record.pathname,
                record.lineno,
                line,
                record.args,
                record.exc_info,
                record.funcName,
            )
            s.append(formatter.format(rec))
        return '\n'.join(s)


class LoggingSubsystem(object):
    def __init__(self, verbosity=INFO, logfile=None):
        self.verbosity = verbosity
        self.logfile = logfile

    def start(self):
        # Configure console logging
        if sys.__stderr__.isatty():
            console_formatter = LevelColoringFormatter("  %(levelname)8s - ",
                                                       "%(message)s")
        else:
            console_formatter = LevelDependentFormatter({
                DEBUG: "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
                INFO: "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
                WARNING: "%(asctime)s - %(levelname)s - %(name)s - "
                "%(pathname"")s:%(lineno)d - %(message)s",
                ERROR: "%(asctime)s - %(levelname)s - %(name)s - "
                "%(pathname)s:%(lineno)d - %(message)s",
                CRITICAL: "%(asctime)s - %(levelname)s - %(name)s - "
                "%(pathname)s:%(lineno)d - %(message)s",
            })

        logging.captureWarnings(True)

        # All console output not explicitly directed to the user should be
        # a log message instead
        self.console_handler = logging.StreamHandler(sys.__stderr__)
        self.console_handler.setFormatter(console_formatter)
        self.console_handler.setLevel(self.verbosity)

        # Buffer the logging until no errors happen
        self.buffered_handler = logging.handlers.MemoryHandler(9999, CRITICAL)
        # Configure file logging
        if self.logfile:
            file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - "
                                               "%(name)s - %(message)s "
                                               "(%(pathname)s:%(lineno)d)")

            # Capture all logging output and write it to the specified log file
            self.file_handler = logging.FileHandler(self.logfile, 'w',
                                                    delay=True)
            self.file_handler.setFormatter(file_formatter)
            self.file_handler.setLevel(logging.ERROR)

            self.buffered_handler.setTarget(self.file_handler)
        else:
            self.file_handler = None

        logger = logging.getLogger()
        logger.setLevel(1)
        logger.addHandler(self.console_handler)
        logger.addHandler(self.buffered_handler)

    def get_logger(self, name):
        logger = logging.getLogger(name)
        logger.pause_stdout_capture = self.pause_stdout_capture
        return logger

    def capture_stdout(self):
        sys.stdout = StdioOnnaStick(logging.getLogger('stdout').info)
        sys.stderr = StdioOnnaStick(logging.getLogger('stderr').info)

    def pause_stdout_capture(self):
        return PrintTo(sys.__stdout__)

    def increment_verbosity(self, steps=1):
        self.verbosity = max(1, self.verbosity - 10 * steps)
        self.console_handler.setLevel(self.verbosity)

        if self.file_handler:
            self.file_handler.setLevel(1)

    def stop(self, status=0):
        if not status:
            self.buffered_handler.setTarget(None)
            self.buffered_handler.close()
        else:
            self.buffered_handler.flush()
            self.buffered_handler.close()

            print >>sys.__stderr__, ''
            if self.logfile:
                print >>sys.__stderr__, (
                    "%s exited with a non-zero exit status (%d). A complete "
                    "log was stored in the %s file." % (sys.argv[0], status,
                                                        self.logfile))
            else:
                print >>sys.__stderr__, (
                    "%s exited with a non-zero exit status (%d)." % (
                        sys.argv[0], status))
