import logbook
from . import hooks

_logger = logbook.Logger(__name__)

class Step(object):
    def __init__(self, msg):
        super(Step, self).__init__()
        self.message = msg
    def __str__(self):
        return self.message
    def __repr__(self):
        return "<Step {0!r}>".format(self.message)
    def _start(self):
        _logger.notice(self.message)
        hooks.step_start()
    def _success(self):
        hooks.step_success()
    def _error(self):
        hooks.step_error()
    def _end(self):
        hooks.step_end()
    def __enter__(self):
        self._start()
        return self
    def __exit__(self, exc_type, exc_value, exc_tb):
        try:
            if exc_type is None:
                self._success()
            else:
                self._error()
        finally:
            self._end()

