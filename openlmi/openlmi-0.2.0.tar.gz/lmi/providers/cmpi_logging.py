# -*- Coding:utf-8 -*-
#
# Copyright (C) 2012-2013 Red Hat, Inc.  All rights reserved.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# Authors: Jan Safranek <jsafrane@redhat.com>
"""
Contains handlers and loggers specific to providers logging running
under cimom.
"""

import logging
import logging.config
import inspect
from itertools import chain
import os
import sys

# Custom logging levels
TRACE_WARNING = logging.INFO - 1
TRACE_INFO = logging.INFO - 2
TRACE_VERBOSE = logging.DEBUG

# Mapping from level name to its number
LOGGING_LEVELS = {
        "critical"      : logging.CRITICAL,
        "error"         : logging.ERROR,
        "warning"       : logging.WARNING,
        "warn"          : logging.WARNING,
        "info"          : logging.INFO,
        "trace_warning" : TRACE_WARNING,
        "trace_info"    : TRACE_INFO,
        "trace_verbose" : TRACE_VERBOSE,
        "debug"         : logging.DEBUG
}

DEFAULT_LOGGING_CONFIG = {
    "version" : 1,
    'disable_existing_loggers' : True,
    "formatters": {
        # this is a message format for logging function/method calls
        # it's manually set up in YumWorker's init method
        "default": {
            "()": "lmi.providers.cmpi_logging.DispatchingFormatter",
            "formatters" : {
                "lmi.providers.cmpi_logging.trace_function_or_method":
                    "%(levelname)s:%(message)s"
                },
            "default" : "%(levelname)s:%(module)s:"
                        "%(funcName)s:%(lineno)d - %(message)s"
            },
        },
    "handlers": {
        "stderr" : {
            "class" : "logging.StreamHandler",
            "level" : "ERROR",
            "formatter": "default",
            },
        "cmpi" : {
            "()"    : "lmi.providers.cmpi_logging.CMPILogHandler",
            # this must be filled with broker env logger
            "cmpi_logger" : None,
            "level" : "ERROR",
            "formatter" : "default"
            },
        },
    "root": {
        "level": "ERROR",
        "handlers" : ["cmpi"],
        },
    }

class DispatchingFormatter(object):
    """
    Formatter class for logging module. It allows to predefine different
    format string for paricular module names.

    There is no way, how to setup this formatter in configuration file.
    """
    def __init__(self, formatters, default):
        """
        *format* in parameters description can be either ``string`` or
        another formatter object.

        :param formatters (``dict``) Mapping of module names to *format*.
        :param default Default *format*.
        """
        for k, formatter in formatters.items():
            if isinstance(formatter, basestring):
                formatters[k] = logging.Formatter(formatter)
        self._formatters = formatters
        if isinstance(default, basestring):
            default = logging.Formatter(default)
        self._default_formatter = default

    def format(self, record):
        """
        Interface for logging module.
        """
        formatter = self._formatters.get(record.name, self._default_formatter)
        return formatter.format(record)

class CMPILogHandler(logging.Handler):
    """
        A handler class, which sends log messages to CMPI log.
    """

    def __init__(self, cmpi_logger, *args, **kwargs):
        self.cmpi_logger = cmpi_logger
        super(CMPILogHandler, self).__init__(*args, **kwargs)

    def emit(self, record):
        msg = self.format(record)
        if record.levelno >= logging.ERROR:
            self.cmpi_logger.log_error(msg)
        elif record.levelno >= logging.WARNING:
            self.cmpi_logger.log_warn(msg)
        elif record.levelno >= logging.INFO:
            self.cmpi_logger.log_info(msg)
        elif record.levelno >= TRACE_WARNING:
            self.cmpi_logger.trace_warn(record.filename, msg)
        elif record.levelno >= TRACE_INFO:
            self.cmpi_logger.trace_info(record.filename, msg)
        elif record.levelno >= logging.DEBUG:
            self.cmpi_logger.trace_verbose(record.filename, msg)

class CMPILogger(logging.getLoggerClass()):
    """
        A logger class, which adds trace_method level log methods.
    """
    def trace_warn(self, msg, *args, **kwargs):
        """ Log message with TRACE_WARNING severity. """
        self.log(TRACE_WARNING, msg, *args, **kwargs)

    def trace_info(self, msg, *args, **kwargs):
        """ Log message with TRACE_INFO severity. """
        self.log(TRACE_INFO, msg, *args, **kwargs)

    def trace_verbose(self, msg, *args, **kwargs):
        """ Log message with TRACE_VERBOSE severity. """
        self.log(TRACE_VERBOSE, msg, *args, **kwargs)

    def _log(self, level, msg, args, exc_info=None, extra=None):
        """
        Overrides ``_log()`` function of basic ``Logger``. The purpose is to
        log tracebacks with different level instead of ERROR to prevent them
        being logged to syslog.
        """
        if logging._srcfile:
            #IronPython doesn't track Python frames, so findCaller throws an
            #exception on some versions of IronPython. We trap it here so that
            #IronPython can use logging.
            try:
                fn, lno, func = self.findCaller()
            except ValueError:
                fn, lno, func = "(unknown file)", 0, "(unknown function)"
        else:
            fn, lno, func = "(unknown file)", 0, "(unknown function)"
        if exc_info:
            if not isinstance(exc_info, tuple):
                exc_info = sys.exc_info()
            record = self.makeRecord(self.name, level, fn, lno, msg, args,
                    None, func, extra)
            self.handle(record)
            record = self.makeRecord(self.name, TRACE_WARNING, fn,
                    lno, str(exc_info[1]), tuple(), exc_info, func, extra)
        else:
            record = self.makeRecord(self.name, level, fn, lno, msg,
                    args, exc_info, func, extra)
        self.handle(record)

logging.setLoggerClass(CMPILogger)

def trace_function_or_method(is_method=False, frame_level=1):
    """
    Factory for function and method decorators. Generated decorators
    log every calls and exits of decorated functions or methods.

    Logged information contain the caller's module and line together with
    called function's module, function name and line number.

    :param is_method: (``bool``) Whether returned decorator is targeted
        for use upon a method of a class. It modified logged function by
        prepending owning class name.
    :param frame_level: (``int``) Number of nested frames to skip when
        searching for called function scope by inspecting stack upwards.
        When the result of this function is applied directly on the definition
        of function, it's value should be 1. When used from inside of some
        other factory, it must be increased by 1.
    """

    assert frame_level >= 1

    def _decorator(func):
        """
        Decorator for logging entries and exits of function or method.
        """
        if not inspect.ismethod(func) and not inspect.isfunction(func):
            raise TypeError("func must be a function")

        def _print_value(val):
            """
            Used here for printing function arguments. Shortens the output
            string, if that would be too long.
            """
            if isinstance(val, list):
                if len(val) < 2:
                    return str(val)
                else:
                    return "[%s, ...]" % _print_value(val[0])
            return str(val)

        module = func.__module__.split('.')[-1]
        frm = inspect.currentframe()
        for _ in range(frame_level):
            frm = frm.f_back
        lineno = frm.f_lineno
        del frm
        classname = inspect.getouterframes(
                inspect.currentframe())[frame_level][3]

        def _wrapper(*args, **kwargs):
            """
            Wrapper for function or method, that does the logging.
            """
            logger = logging.getLogger(__name__+'.trace_function_or_method')
            logargs = {}
            if logger.isEnabledFor(logging.DEBUG):
                frm = inspect.currentframe()
                logargs.update({
                    "caller_file" : os.path.basename(os.path.splitext(
                        frm.f_back.f_code.co_filename)[0]),
                    "caller_lineno" : frm.f_back.f_lineno,
                    "module" : module,
                    "func"   : classname + "." + func.__name__
                        if is_method else func.__name__,
                    "lineno" : lineno,
                    "action" : "entering",
                    "args"   : ", ".join(chain(
                                (_print_value(a) for a in args),
                                (   "%s=%s"%(k, _print_value(v))
                                for k, v in kwargs.items())))
                })

                if not logargs["args"]:
                    logargs["args"] = ""
                else:
                    logargs["args"] = " with args=(%s)" % logargs["args"]
                logger.debug("%(caller_file)s:%(caller_lineno)d - %(action)s"
                    " %(module)s:%(func)s:%(lineno)d%(args)s" , logargs)
            try:
                result = func(*args, **kwargs)
                if logger.isEnabledFor(logging.DEBUG):
                    logargs["action"] = "exiting"
                    logger.debug("%(caller_file)s:%(caller_lineno)d"
                        " - %(action)s %(module)s:%(func)s:%(lineno)d",
                        logargs)
            except Exception as exc:
                if logger.isEnabledFor(logging.DEBUG):
                    logargs['action'] = 'exiting'
                    logargs['error'] = str(exc)
                    logger.debug("%(caller_file)s:%(caller_lineno)d"
                        " - %(action)s %(module)s:%(func)s:%(lineno)d"
                        " with error: %(error)s", logargs)
                raise
            return result

        return _wrapper

    return _decorator

def trace_function(func, frame_level=1):
    """ Convenience function used for decorating simple functions. """
    return trace_function_or_method(frame_level=frame_level + 1)(func)

def trace_method(func, frame_level=1):
    """ Convenience function used for decorating methods. """
    return trace_function_or_method(True, frame_level + 1)(func)

def setup(env, config, default_logging_dict=None):
    """
    Set up the logging with options given by SoftwareConfiguration instance.
    This should be called at process's startup before any message is sent to
    log.

    :param env: (``ProviderEnvironment``) Provider environment, taken
        from CIMOM callback (e.g. ``get_providers()``).
    :param config: (``BaseConfiguration``) Configuration with Log section
        containing settings for logging.
    :param default_logging_dict: (``dict``) Dictionary with default logging
        configuration. If ``None``, ``DEFAULT_LOGGING_CONFIG`` will be used. If
        given, it must contain at least "root" entry for root logger and
        predefined "cmpi" and "stderr" handlers for logging to CIMOM and to
        stderr.
    """
    cp = config.config
    logging_setup = False
    try:
        path = config.file_path('Log', 'FileConfig')
        if not os.path.exists(path):
            logging.getLogger(__name__).error('given FileConfig "%s" does'
                    ' not exist', path)
        else:
            logging.config.fileConfig(path)
            logging_setup = True
    except Exception:
        if cp.has_option('Log', 'FileConfig'):
            logging.getLogger(__name__).exception(
                    'failed to setup logging from FileConfig')
    if logging_setup is False:
        if default_logging_dict is None:
            defaults = DEFAULT_LOGGING_CONFIG.copy()
        else:
            defaults = default_logging_dict
        defaults["handlers"]["cmpi"]["cmpi_logger"] = env.get_logger()
        if config.stderr:
            defaults["root"]["handlers"].append("stderr")
        level = config.logging_level
        if not level in LOGGING_LEVELS:
            logging.getLogger(__name__).error(
                    'level name "%s" not supported', level)
        else:
            level = LOGGING_LEVELS[level]
            for handler in defaults["handlers"].values():
                handler["level"] = level
            defaults["root"]["level"] = level
        logging.config.dictConfig(defaults)

class LogManager(object):
    """
        Class, which takes care of CMPI logging.
        There should be only one instance of this class and it should be
        instantiated as soon as possible, even before reading a config.
        The config file can be provided later by set_config call.

        Use of this manager is an alternative to single call to ``setup()``
        function of this module.
    """

    def __init__(self, env):
        """
            Initialize logging.
        """
        self._env = env
        self._config = None

    @property
    def config(self):
        """ Provider configuration object. """
        return self._config
    @config.setter
    def config(self, config):
        """
            Set a configuration of logging. It applies its setting immediately
            and also subscribes for configuration changes.
        """
        self._config = config
        config.add_listener(self._config_changed)
        # apply the config
        self._config_changed(config)

    @property
    def cmpi_handler(self):
        """ Returns cmpi log handler passing logged messages to cimom. """
        for handler in logging.getLogger('').handlers:
            if isinstance(handler, CMPILogHandler):
                return handler
        return CMPILogHandler(self._env.get_logger())

    @trace_method
    def _config_changed(self, config):
        """
            Apply changed configuration, i.e. start/stop sending to stderr
            and set appropriate log level.
        """
        setup(self._env, config)

    def destroy(self):
        """
            Shuts down the logging framework. No logging can be done
            afterwards.
        """
        logging.getLogger(__name__).debug('shutting down logging')
        logging.shutdown()

def get_logger(module_name):
    """
    Convenience function for getting callable returning logger for particular
    module name. It's supposed to be used at module's level to assign its
    result to global variable like this:

        LOG = cmpi_logging.get_logger(__name__)

    This can be used in module's functions and classes like this:

        def module_function(param):
            LOG().debug("this is debug statement logging param: %s", param)

    Thanks to ``LOG`` being a callable, it always returns valid logger object
    with current configuration, which may change overtime.
    """
    def _logger():
        """ Callable used to obtain current logger object. """
        return logging.getLogger(module_name)
    return _logger
