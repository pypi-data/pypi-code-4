""" Entry point for daemon """
from .daemon import Daemon
from .logger import objectLogger


def server(func, params):
    """ Provides handler for logs """
    def logger():
        func(params)
    return logger


def logger_main(args, **kw):
    """ Entry point for logger script """
    if not len(args) > 1:
        return

    daemon = Daemon(
        'pidfile',
        server(objectLogger, kw),
        home_dir=kw['main_dir'],
        stdout='output',
        stderr='error'
    )
    if args[1] == 'start':
        daemon.start()
    elif args[1] == 'stop':
        daemon.stop()
    elif args[1] == 'restart':
        daemon.restart()
    elif args[1] == 'status':
        daemon.status()
