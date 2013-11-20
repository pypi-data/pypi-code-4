#!/usr/bin/env python
# coding: utf-8
"""
Logging
"""

# Python Standard Library
import importlib
import inspect
import sys
import types

#
# Metadata
# ------------------------------------------------------------------------------
#
__name__ = "logfile"
__author__ = u"Sébastien Boisgérault <Sebastien.Boisgerault@mines-paristech.fr>"
__license__ = "MIT License"
__url__     = "https://github.com/boisgera/logfile"
__version__ = "0.1.0-alpha.1"
__classifiers__ = """
Intended Audience :: Developers
Operating System :: OS Independent
Programming Language :: Python :: 2.7
License :: OSI Approved :: MIT License
Topic :: Software Development :: Libraries :: Python Modules
Topic :: System :: Logging
"""

# ------------------------------------------------------------------------------
# TODO: *shared* configuration between all loggers to make logging cooperative.
#
# Design: given that all existing loggers shall *implicitly* refer to the config
#         (that holds for example the verbosity level), we have no choice
#         but to have a global module-level variable here. However, a user
#         of the logger module that intends to play nice and not scramble other
#         logger users may need some get/set config functions.       

# Doc: the global _Config instance has the following properties: 
#      - 'level' is a verbosity level: the higher it is, the more gets printed.
#      - 'output' is the common loggers output file object,
#      - 'format' is the customizable message formatting method. It may use
#        (the source logger object and) the message logged.
#      - [TODO]: 'filters': I'd like to have the way to specify a set of
#        (positive or negative ?) filters that may filter according to the
#        hierarchy of loggers context (say 'mystuff.deeper.blah') optionnaly
#        inferred at loggers creation time by the __main__ variable ?
#        CARE: this inference won't work if the module is used as a script ...

# TODO: generalize the context so that we may say for example that we are in
#       audio.wave.write (function write in the audio.wave module) ? Dynamic
#       contexts ? That would be nice and quite easy I guess if I use
#       context managers.
#
# TODO: document automatic substitution of local variables in messages.
#
# TODO: have a look at 
# <http://stackoverflow.com/questions/4492559/python-code-to-get-current-function-into-a-variable> to get the (qualified) name of a function/method
# that is currently executed. Use it as an info for the logger context and
# drop explicit context naming ? Migrate the standard logfiles to the
# module toplevel ?

# TODO: register modules: build a code to qualified name map.

# TODO: use the inspiration from warnings module to extract more info from
#       the point of call (module, that could be the default tag, line, etc.)
#       Probably use the module info as the default tagging information to
#       limit the need for manual tagging ? By a suitable exploration of the
#       code object, we can even get to the function name. Would it work
#       for methods (get the class name ?). Nope. Same issue for methods
#       that we have for profiling, would require (SOME) source file
#       analysis (and does not always work ...). What about generated methods
#       or methods added in a class after its definition ? (Would not work
#       with source analysis right ?). Do the opposite and inspect all methods
#       of all classes in a module to identify them by code (code object I
#       mean) ? But that won't work with decorators or generated functions ...
#       I am not sure how, i should deal with that issue (and I am not sure
#       that both issues are the same). With an explicit
#       "logfile.tag" context manager ?
#       Mmm even for inner function, we still have the name. And that may
#       be good enough ? Otherwise we could find something with the lineno
#       if it is in the range of a function def or decorator ? And here,
#       we would have little choice but parsing ? Use getsourcelines from
#       inspect to do the job ? Use syntaxic analysis on top of that ?
#       Well maybe in a first approach, only deal with classes ? Or dont
#       even bother ?
#
#       Rk: it's hard to implement a system in which manual tagging can
#           override the automatic tagging ... How do we know if the
#           tagging was set for the current function or the previous one
#           in the call stack ? Fully automatic would be better ... (?)

# TODO: study the warnings API. Disable the warnings by default ? (would be
#       kind of redundant ?). Yes, but only in logfile.warning calls, restore
#       the filter state after that. Implement pre-post hooks as context
#       managers ?

# TODO: implement the full local / global / builtin namespaces in templating.

#
# Logger API
# ------------------------------------------------------------------------------
#

class LogFile(int):
    """
    LogFiles are files used to log messages.

    TODO: talk about the level / int stuff and configuration after the
          files properties ?

    LogFiles also behave like integers: the number they represent denotes how 
    important their messages are. The lower the logfile number, the more 
    important the logfile. Five standard log files are defined:

        >>> import logger
        >>> names = "critical error warning info debug"
        >>> for name in names.split():
        ...     logfile = getattr(logger, name)
        ...     print "{0:>8}: {1:>2}".format(name, int(logfile))
        critical: -2
           error: -1
         warning:  0
            info:  1
           debug:  2

    **TODO: migrate the config.level discussion to the config part, with
    format and output discussion**

    A message written into a logfile will effectively get logged only 
    if the logfile number is less or equal to the current verbosity 
    (`config.level`). For example, with the default logger 
    verbosity (`0`), only messages send to the `critical`, `error` 
    and `warning` logfiles will logged. As logfiles are integers, they
    may be used directly to change the logger verbosity: the code

        >>> logger.config.level = logger.info

    will increase the verbosity to `1`, so that the messages to the `info`
    are now logged. **TODO: test before after**

    #### Writing into LogFiles

    To demonstrate how logging works, we first make sure that the output of
    the logfiles are `sys.stdout` instead of the default `sys.stderr`

        >>> import sys
        >>> logger.config.output = sys.stdout

    Messages can be send to logfiles in two ways: either using the file 
    interface, such as in:

        >>> print >> logger.warning, "I feel a disturbance in the Force."
        I feel a disturbance in the Force.

    or using the callable interface:

        >>> logger.warning("I feel a disturbance in the Force.")
        I feel a disturbance in the Force.


    The former call is handy to quicky convert a code full of  `print` 
    statements without any hierarchy into the `logger` style 
    of logging. 

    #### Message Variables 

    The message send to logfiles often depends on the value of some local
    variables. To simplify this use case, we may refer to local variables
    in messages with the same curly brace syntax use by the 
    [string.format method][format]. The value of the variable will be
    automatically substituted into the message. For example:

        >>> jedi = "Luke"
        >>> logger.info("Use the Force, {jedi}.")
        Use the Force, Luke.

    [format]: http://docs.python.org/library/string.html#formatstrings

    #### LogFile Hooks

    LogFile hooks are an easy way to trigger some action when some message
    is sent to a logfile. A typical use case is to automatically raise an 
    Exception when a message is sent to the `error` logfile:

    First, we disable logging of `error` messages and set the exception hook:

        >>> logger.config.level = logger.critical
        >>> def raise_exception(message):
        ...     raise Exception(message)
        >>> logger.error.set_hook(raise_exception)

    Now, if we use the logfile `logger.error`, we obtain:

        >>> logger.error("I feel a great disturbance in the Force.")
        Traceback (most recent call last):
        ...
        Exception: I feel a great disturbance in the Force.

    LogFile hooks will use extra arguments in logfile calls, for example:

        >>> def raise_exception(message, type=Exception):
        ...     raise type(message)
        >>> logger.error.set_hook(raise_exception)
        >>> class ForceError(Exception):
        ...     pass
        >>> logger.error("I feel a great disturbance in the Force.", ForceError)
        Traceback (most recent call last):
        ...
        ForceError: I feel a great disturbance in the Force.
"""
    def __new__(cls, name, number):
        return int.__new__(cls, number)
    def __init__(self, name, number):
        self.name = name
        self._data = []
        self._hooks = []
    def set_hook(self, *hooks):
        "Install logfile post-write hooks"
        self._hooks = list(hooks)
    def write(self, message):
        # this do-nothing code ensures that when the user calls either
        # `__call__` or `write`, it will go through exactly one extra
        # function call before `inspect.stack` is called in `write`.
        self._write(message)
    def __call__(self, message, *args, **kwargs):
        self._write(message, *args, **kwargs)
        self._write("\n", *args, **kwargs)
    def _write(self, message, *args, **kwargs): 
        # the locals() from the user code are always 2 frames away.
        # ISSUE: when logger logfiles are used from Cython code, 
        #        there is no corresponding frame and we can't get
        #        to the locals ... we end up with a 'ValueError' 
        #        instead. 
        # Detect that frames do not work, let the use know about it ?
        # Let him enable/disable frame + locals() magic based on this
        # information ? That sucks ... writing two versions of the same
        # code is not a solution !

        # TODO: delay the inspect hackery until we know that we have to
        #       write something (performance reasons) or that some hooks
        #       require us to evaluate the message.

        try:
            frame = inspect.currentframe(2)
            module = inspect.getmodule(frame.f_code) # TODO: manage None
            if module is None:
                prefix = ""
            else:
                prefix = module.__name__ + "."

            # TODO: manage "apps" (__main__ prefix ?) ?

            print frame.f_code.co_name , ">>>"
            name = prefix + frame.f_code.co_name
            #module = frame.f_code.__module__
            locals_ = frame.f_locals
            message = str(message).format(**locals_)
        except ValueError: # can't get the calling function frame.
            message = str(message) # really ? C'mon ...

        self._data.append(message)
        while True:
            # really log something if a call with the "\n" argument is
            # found, otherwise, just format and store the message.
            # The print statements without a trailing comma will generate
            # such a newline and every call to __call__ also does, so
            # only prints with a trailing comma will be stacked. 
            try:
                index = self._data.index("\n")
            except ValueError:
                break
            # Should we chop of the trailing newline ? It kinda sucks
            # with the error hook for example ... yeah, do that and
            # modify the config.format accordingly.
            message = "".join(self._data[:index])
            if config.level >= self:
                #tag_ = tag._tags.get(frame.f_code)
                # tag_ = tag.get_current()
                config.output.write(config.format(self, message, name))
                try:
                    config.output.flush()
                except AttributeError:
                    pass
            for hook in self._hooks:
                hook(message, *args, **kwargs)
            self._data = self._data[index+1:]
    def __str__(self):
        return self.name
    __repr__ = __str__ # do something else ? 

critical = LogFile("critical", -2) 
error    = LogFile("error"   , -1)
warning  = LogFile("warning" ,  0)
info     = LogFile("info"    ,  1)
debug    = LogFile("debug"   ,  2)  

class Config(object):
    """
    Logging Configuration
    """
    def __init__(self, level=None, output=None, format=None):
        """
        The members of a `Config` instance are:

        `level:`
          : is verbosity level: the higher it is, the more gets logged,
        `output:`
          : the common logger logfiles output file object,
        `format:` 
          : the customizable message formatting function whose
            arguments are:
            
            `logfile:`
              : the logfile that requested the logging, 
            `message:`
              : the message logged.
        """
        self.level = level or 0
        self.output = output or sys.stderr
        self.format = format or self._format
    def _format(self, logfile, message, tag):
        return message + "\n"

config = Config()

# TODO: provide a choice of formatters ?

#
# Tagging
# -------
#

# This is too much magic. I kinda like the code to tag stuff that allows
# tag persistence and the fact that you cant tag the code you cant edit and
# the auto "remove-tag" at the end of the function and even multi-tag a 
# given section (may be handy for large functions that you don't want to
# split just yet). And we cant even tag nested functions, use DYNAMIC tags
# and so on. (Uhu there may be some issue with nested functions ...).
# Expliciteness also solves the "used as a script" naming issue.
# But the "I ain't really a module" is too much. Plus, there is some overhead
# for every attribute access ...
# The only good point about the current config is the `logger.tag += "stuff"`
# shortcut. Is the use case that important ? Use a tag FUNCTION instead ?

# TODO: document

# TODO: support context manager AND decorator style.

# TODO: experiment with Cython (ouch).

# BUG: function with code / tag / code / tag / code: when we come back into
#      the function, the 2nd tag is active.

# Rk: the current "same code or no log" policy plays badly with decorators ...

# TODO: Think of static methods and a stack policy for active tags ???

class tag(object):
    #_tags = {} # tags, indexed by code object.
    _tags = []

    @staticmethod
    def get_current():
        if tag._tags:
            return tag._tags[-1]

    def __init__(self, name=None):
        self.name = name
    def __enter__(self):
        tag._tags.append(self.name)
    def __exit__(self, exc_type=None, exc_value=None, traceback=None):
        tag._tags.pop()
    def __call__(self, function):
        # see <http://www.python.org/dev/peps/pep-0343/>
        enter = lambda: self.__enter__()
        exit  = lambda: self.__exit__()
        def _function(*args, **kwargs):
            enter()
            exc = True
            try:
                try:
                    return function(*args, **kwargs)
                except:
                    exc = False
                    if not exit():
                        raise
            finally:
                if exc:
                    exit()
        # TODO: decoration scrambles docgen, solve that.
        #       begin by restoring the function signature.
        #       consider using the technique of the 'decorator' 
        #       module.
        #       We're probably missing the lineinfo data used by docgen
        #       to find and layout the function doc ... Are they writable,
        #       can we restore them ? OOOOOOOk, we end up with a reference
        #       to the decorated function, whose source lives in the decorator
        #       (here logging) module. Only a syntax based analysis of the
        #       source file will save us I'm afraid ... 
        _function.__name__ = function.__name__
        _function.__doc__ = function.__doc__
        return _function

# tmp
def _format(logfile, message, tag):
    tag = tag or ""
    return " {0!r:<9} | {1:<16} | {2}\n".format(logfile, tag, message)

config.format = _format

if __name__ == "__main__":
    import doctest
    doctest.testmod()

