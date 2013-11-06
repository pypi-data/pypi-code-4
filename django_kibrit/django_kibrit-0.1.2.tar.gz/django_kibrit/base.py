from os import name
import os
from subprocess import Popen, PIPE
import sys

from django.core.cache import cache

from django_kibrit.constants import DJANGO_KIBRIT_CACHED_KEY_ID


class GitRevision(object):
    """
    Return the 8 character long git revision number or an empty string
    """

    _revision = None

    def __init__(self, path=None):
        """
        Get the cached tag for the cached key id. Otherwise create your own
        """
        self.path = path or self.find_git()

    @property
    def revision(self):
        """
        Get current revision
        """
        self.init_repo()
        cache.set(DJANGO_KIBRIT_CACHED_KEY_ID, self._revision, 60)
        return self._revision

    def init_repo(self):
        """
        The command to run and tag to return
        """
        try:
            self._revision = self.git('git describe --always --tags')
        except Exception, err:
            self._revision = ''

    def git(self, command=None, stderr=PIPE, stdout=PIPE, **kwargs):
        """
        Run a subprocess for the git command.
        """
        try:
            proc = Popen(
                command.split(), stderr=stderr, stdout=stdout,
                close_fds=(name == 'posix'), cwd=self.path, **kwargs)

        except Exception, err:
            pass
        try:
            output, error= [s.strip() for s in proc.communicate()]
        except Exception, err:
            output, error = '', ''
        return output

    def find_git(self, **kwargs):
        """
        Recursively finds a file directory named .git
        """
        command = "find -L ../src/ -type d -name .git".split()
        # TODO: can be made easier with __file__ and/or __name__
        command[2] = kwargs.get('path') or os.path.join(os.path.realpath(os.path.dirname(sys.argv[0])), '../src/')
        command[6] = kwargs.get('pattern') or command[6]
        try:
            proc = Popen(command, stderr=PIPE, stdout=PIPE,
                         close_fds=(name == 'posix'), cwd=os.path.dirname(command[2]), **kwargs)
        except Exception, err:
            pass
        try:
            output, error= [s.strip() for s in proc.communicate()]
        except Exception, err:
            output, error = '', ''
        return output
