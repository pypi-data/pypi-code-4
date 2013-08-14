"""
lminit.recipes.recipe
~~~~~

:copyright: (c) 2010-2013 by Luis Morales
:license: BSD, see LICENSE for more details.
"""

import os
import subprocess
import shlex

from cli import green, blue, cyan


class Module(object):
    """
    Base class for module packages
    """

    temp = '/tmp'

    def __init__(self, user):
        self.user = user
        self.home = os.path.expanduser('~' + user)
        assert os.path.exists(self.home)

    def is_valid(self):
        raise NotImplementedError()

    def banner(self):
        """text progress separator"""
        print cyan('****************************************************************')

    def message(self, string):
        print blue('- ' + string)

    def progress(self, string):
        print green('\t* ' + string)

    def run(self, command, as_root=True):
        fnull = open(os.devnull, 'w')
        parts = shlex.split(command)
        args = parts if as_root else ['sudo', '-u', self.user] + parts
        result = subprocess.call(args, stdout=fnull, stderr=fnull)
        fnull.close()
        return result

    def is_success(self, command, as_root=True):
        return self.run(command, as_root) == 0

    def install_package(self, name):
        return self.run('apt-get install -y ' + name)

    def add_apt_repo(self, name):
        return self.run('add-apt-repository -y ' + name + ' && apt-get update')

    def remove_package(self, name):
        return self.run('apt-get remove -y ' + name)

    def replace_text(self, filename, old, new, as_root=True):
        command = 'sed -i "s/%s/%s/" %s' % (old, new, filename)
        self.run(command, as_root)

    def append_text(self, filename, text=''):
        with open(filename, "a") as _file:
            _file.write(text + '\n')

    def wget(self, url, as_root=True):
        command = "wget -q --no-check-certificate " + url
        return self.run(command, as_root)

    def is_ok(self, string):
        result = raw_input(string + '? [y/n]\n').strip().lower()
        if result == 'y':
            return True
        if result == 'n':
            return False
        return self.is_ok(string)

    def execute(self):
        """
        Default module method
        """
        raise NotImplementedError()

    def __repr__(self):
        return '%s: user=%r, home=%r' % (self.__class__.__name__, self.user, self.home)
