import os
import sys
import StringIO
from tempfile import TemporaryFile

from numpy.distutils import exec_command


def fake_with(context, f, *args, **kwargs):
    context.__enter__()
    try:
        f(*args, **kwargs)
    finally:
        context.__exit__(None, None, None)

class redirect_stdout(object):
    """Context manager to redirect stdout for exec_command test."""
    def __init__(self, stdout=None):
        self._stdout = stdout or sys.stdout

    def __enter__(self):
        self.old_stdout = sys.stdout
        sys.stdout = self._stdout

    def __exit__(self, exc_type, exc_value, traceback):
        self._stdout.flush()
        sys.stdout = self.old_stdout
        # note: closing sys.stdout won't close it.
        self._stdout.close()

class redirect_stderr(object):
    """Context manager to redirect stderr for exec_command test."""
    def __init__(self, stderr=None):
        self._stderr = stderr or sys.stderr

    def __enter__(self):
        self.old_stderr = sys.stderr
        sys.stderr = self._stderr

    def __exit__(self, exc_type, exc_value, traceback):
        self._stderr.flush()
        sys.stderr = self.old_stderr
        # note: closing sys.stderr won't close it.
        self._stderr.close()

class emulate_nonposix(object):
    """Context manager to emulate os.name != 'posix' """
    def __init__(self, osname='non-posix'):
        self._new_name = osname

    def __enter__(self):
        self._old_name = os.name
        os.name = self._new_name

    def __exit__(self, exc_type, exc_value, traceback):
        os.name = self._old_name


def test_exec_command_stdout():
    # Regression test for gh-2999 and gh-2915.
    # There are several packages (nose, scipy.weave.inline, Sage inline
    # Fortran) that replace stdout, in which case it doesn't have a fileno
    # method.  This is tested here, with a do-nothing command that fails if the
    # presence of fileno() is assumed in exec_command.

    # The code has a special case for posix systems, so if we are on posix test
    # both that the special case works and that the generic code works.

    # Test posix version:
    fake_with(redirect_stdout(StringIO.StringIO()),
        fake_with, redirect_stderr(TemporaryFile()),
            exec_command.exec_command, "cd '.'")

    if os.name == 'posix':
        # Test general (non-posix) version:
        fake_with(emulate_nonposix(),
            fake_with, redirect_stdout(StringIO.StringIO()),
                fake_with, redirect_stderr(TemporaryFile()),
                    exec_command.exec_command, "cd '.'")

def test_exec_command_stderr():
    # Test posix version:
    fake_with(redirect_stdout(TemporaryFile(mode='w+')),
        fake_with, redirect_stderr(StringIO.StringIO()),
            exec_command.exec_command, "cd '.'")

    if os.name == 'posix':
        # Test general (non-posix) version:
        fake_with(emulate_nonposix(),
            fake_with, redirect_stdout(TemporaryFile()),
                fake_with, redirect_stderr(StringIO.StringIO()),
                    exec_command.exec_command, "cd '.'")
