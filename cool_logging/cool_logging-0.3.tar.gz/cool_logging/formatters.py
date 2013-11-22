"""
:author: samu
:created: 2/20/13 7:11 PM
"""
from UserDict import DictMixin
from string import Template

import logging

from termcolor import colored


# LOG_FORMAT_CONSOLE_COLOR = \
#     "%(c_date)s %(c_leveltag)s %(c_name)s %(c_function)s\n%(indented_message)s"
LOG_FORMAT_CONSOLE_COLOR = \
    u"${c_leveltag} ${c_name} in ${c_function} at ${c_date}\n${prefixed_message}"
LOG_DATEFMT_CONSOLE_COLOR = u"%F %T"


def _colorer(*args, **kwargs):
    return lambda x: colored(x, *args, **kwargs)


class LazyRecordColorer(DictMixin):
    colorers = {
        logging.DEBUG: _colorer('cyan', 'on_blue', attrs=['bold']),
        logging.INFO: _colorer('yellow', 'on_green', attrs=['bold']),
        logging.WARNING: _colorer('white', 'on_yellow', attrs=['bold']),
        logging.ERROR: _colorer('white', 'on_red', attrs=['bold']),
        logging.CRITICAL: _colorer('yellow', 'on_red', attrs=['bold']),
    }

    text_colorers = {
        logging.DEBUG: _colorer('white'),
        logging.INFO: _colorer('green'),
        logging.WARNING: _colorer('yellow'),
        logging.ERROR: _colorer('red'),
        logging.CRITICAL: _colorer('red', attrs=['bold']),
    }

    leveltags = {
        logging.DEBUG: u"DBUG",
        logging.INFO: u"INFO",
        logging.WARNING: u"WARN",
        logging.ERROR: u"ERR!",
        logging.CRITICAL: u"CRIT",
    }

    _extra_fields = [
        'c_date',
        'c_asctime',
        'c_leveltag',
        'c_levelname',
        'c_name',
        'c_function',
        'indented_message',
        'wrapped_message',
        'prefixed_message'
    ]

    def __init__(self, record):
        self.record = record

    def __getitem__(self, item):
        if item not in self.keys():
            raise KeyError(item)

        if item in self._extra_fields:
            return getattr(self, item)

        return self.record.__dict__[item]

        # return getattr(self.record, item)
        # return self.record.__dict__[item]

    def __getattr__(self, item):
        return self.record.__dict__[item]

    def keys(self):
        return self._extra_fields + self.record.__dict__.keys()

    @property
    def c_date(self):
        return colored(
            u'{},{:03d}'.format(self.asctime, int(self.msecs)),
            'cyan')

    @property
    def c_asctime(self):
        return colored(self.record.asctime, 'cyan')

    @property
    def c_leveltag(self):
        colorer = self.colorers.get(self.record.levelno, lambda x: x)
        return colorer(' %s ' % self.leveltags.get(self.record.levelno, '????'))

    @property
    def c_levelname(self):
        colorer = self.colorers.get(self.record.levelno, lambda x: x)
        return colorer(' %s ' % self.record.levelname)

    @property
    def c_name(self):
        return colored(' %s ' % self.record.name, 'white', 'on_magenta', attrs=['bold'])

    @property
    def c_function(self):
        return u'{}.{}'.format(
            colored(self.module, 'green'),
            colored(self.funcName, 'green', attrs=['bold']),
        )

    @property
    def colored_message(self):
        colorer = self.text_colorers.get(self.record.levelno) or (lambda x: x)
        lines = self.record.getMessage().splitlines()
        return u"\n".join(colorer(l) for l in lines)

    @property
    def indented_message(self):
        lines = self.record.getMessage().splitlines()
        return u"\n".join(u"    {}".format(l) for l in lines)

    @property
    def prefixed_message(self):
        c_levelname = self.c_leveltag
        # colorer = self.text_colorers.get(self.record.levelno) or (lambda x: x)
        lines = self.record.getMessage().splitlines()
        return u"\n".join(u"{}     {}".format(c_levelname, l) for l in lines)

    @property
    def wrapped_message(self):
        from textwrap import TextWrapper
        lines = self.record.getMessage().splitlines()
        new_lines = []
        w = TextWrapper(width=66)  # 70 - 4
        for line in lines:
            for _line in w.wrap(line):
                new_lines.append(_line)
        return u"\n".join([u"    %s" % l for l in new_lines])


class ConsoleColorFormatter(logging.Formatter):
    """
    A nice color formatter for the logging module, providing some extra
    context arguments for the log output:

    c_date
        The colored full date (``%(asctime)s,%(msecs)03d``)

    c_asctime
        The colored ``asctime``

    c_leveltag
        The colored level "tag"

    c_levelname
        The colored level name

    c_name
        The colored logger name (``[%(name)s]``)

    c_function
        The colored module/function name (``%(module)s.%(funcName)s``)

    indented_message
        The message, wrapped to fit 70 columns and indented by four spaces.
    """

    def __init__(self, fmt=None, datefmt=None, newstyle=False):
        if fmt is None:
            fmt = LOG_FORMAT_CONSOLE_COLOR
            newstyle = True
        if datefmt is None:
            datefmt = LOG_DATEFMT_CONSOLE_COLOR
        super(ConsoleColorFormatter, self).__init__(fmt=fmt, datefmt=datefmt)
        self._newstyle = newstyle
        if newstyle:
            self._tpl = Template(self._fmt)

    def format(self, record):
        record.message = record.getMessage()
        record.asctime = self.formatTime(record, self.datefmt)

        if self._newstyle:
            # lcr = LazyRecordColorer(record)
            # import pdb; pdb.set_trace()
            # formatted_record = self._fmt.format(LazyRecordColorer(record))
            formatted_record = self._tpl.substitute(LazyRecordColorer(record))

        else:
            formatted_record = self._fmt % LazyRecordColorer(record)

        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)

        if record.exc_text:
            if formatted_record[-1:] != "\n":
                formatted_record += "\n"
            formatted_record += record.exc_text

        return formatted_record
