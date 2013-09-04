import logging
import sys
import cStringIO
from django.views.debug import ExceptionReporter
import traceback as traceback_mod


class DBLogHandler(logging.Handler):
    def emit(self, record):
        from .models import AccessLogEntry

        kwargs = {
            'logger': record.name,
            'level': record.levelno,
            'message': record.getMessage(),
            'module': record.module,
            'pathname': record.pathname,
            'filename': record.filename,
            'lineno': record.lineno,
            'func_name': record.funcName,
            'thread': record.thread,
            'thread_name': record.threadName,
            'process': record.process,
            'process_name': record.processName,
        }
        AAAAA = record.exc_info
        if record.exc_info:
            # sio = cStringIO.StringIO()
            # traceback_mod.print_exception(record.exc_info[0], record.exc_info[1], record.exc_info[2], None, sio)
            exception, traceback = record.exc_info[1:3]
            # exception = None
            if not exception:
                exc_type, exc_value, traceback = sys.exc_info()
            else:
                exc_type = exception.__class__
                exc_value = exception
            reporter = ExceptionReporter(None, exc_type, exc_value, traceback)
            # frames = reporter.get_traceback_frames()
            tb_message = '\n'.join(traceback_mod.format_exception(exc_type, exc_value, traceback))
            kwargs.update({'class_name': exc_type.__name__,
                           'traceback': tb_message})

        AccessLogEntry.objects.create(**kwargs)
