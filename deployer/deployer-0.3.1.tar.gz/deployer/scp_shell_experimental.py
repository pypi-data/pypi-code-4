from deployer.cli import CLInterface, Handler, HandlerType
from deployer.console import Console
from deployer.host import Host
from deployer.host import LocalHost
from deployer.utils import esc1
from termcolor import colored

import sys
import os
import stat
import os.path

# Types

class BuiltinType(HandlerType):
    color = 'cyan'

class LocalType(HandlerType):
    color = 'green'

class RemoteType(HandlerType):
    color = 'yellow'

class ModifyType(HandlerType):
    color = 'red'

class DirectoryType(HandlerType):
    color = 'blue'

class FileType(HandlerType):
    color = None


class CacheMixin(object):
    """
    Mixin for Host, which adds caching to listdir and stat.
    (This makes autocompletion much faster.
    """
    def __init__(self, *a, **kw):
        super(CacheMixin, self).__init__(*a, **kw)
        self._listdir_cache = {}
        self._stat_cache = {}

    def listdir(self):
        cwd = self.getcwd()
        if cwd not in self._listdir_cache:
            self._listdir_cache[cwd] = super(CacheMixin, self).listdir()
        return self._listdir_cache[cwd]

    def stat(self, path):
        cwd = self.getcwd()
        if (cwd, path) not in self._stat_cache:
            self._stat_cache[(cwd, path)] = super(CacheMixin, self).stat(path)
        return self._stat_cache[(cwd, path)]

    def fill_cache(self, pty):
        """ Fill cache for current directory. """
        console = Console(pty)
        with console.progress_bar('Reading directory content...', clear_on_finish=True) as p:
            # Loop through all the files, and call 'stat'
            content = self.listdir()
            p.expected = len(content)

            for f in content:
                p.next()
                self.stat(f)

# Handlers

class SCPHandler(Handler):
    def __init__(self, shell):
        self.shell = shell

#def remote_handler(files_only=False, directories_only=False):
#    """ Create a node system that does autocompletion on the remote path. """
#    return _create_autocompleter_system(files_only, directories_only, RemoteType,
#            lambda shell: shell.host)
#
#
#def local_handler(files_only=False, directories_only=False):
#    """ Create a node system that does autocompletion on the local path. """
#    return _create_autocompleter_system(files_only, directories_only, LocalType,
#            lambda shell: shell.localhost)


class AutocompleteSystem(object):
    files_only = False
    directories_only = False

    def __init__(self, handler_type_cls, get_host_func, is_local):
        self._handler_type_cls = handler_type_cls
        self._get_host_func = get_host_func
        self.is_local = is_local

    def run(self, shell, host, path):
        raise NotImplementedError

    @classmethod
    def create_local(cls):
        return cls._create(cls(LocalType, lambda shell: shell.localhost, True))

    @classmethod
    def create_remote(cls):
        return cls._create(cls(RemoteType, lambda shell: shell.host, False))

    @classmethod
    def _create(cls, system):
        class ChildHandler(SCPHandler):
            is_leaf = True

            def __init__(self, shell, path):
                self.path = path
                SCPHandler.__init__(self, shell)

            @property
            def handler_type(self):
                host = system.get_host_func(self.shell)
                if self.path in ('..', '.', '/') or host.stat(self.path).is_dir:
                    return DirectoryType()
                else:
                    return FileType()

            def __call__(self):
                system.run(self.shell, system.get_host_func(self.shell), self.path)

        class MainHandler(SCPHandler):
            handler_type = system.handler_type_cls()

            def complete_subhandlers(self, part):
                host = system.get_host_func(self.shell)

                for f in host.listdir():
                    if f.startswith(part):
                        if system.files_only and not host.stat(f).is_file:
                            continue
                        if system.directories_only and not host.stat(f).is_dir:
                            continue

                        yield f, ChildHandler(self.shell, f)

                # Root, current and parent directory.
                for name in ('/', '..', '.'):
                    if name.startswith(part) and not system.files_only:
                        yield name, ChildHandler(self.shell, name)

            def get_subhandler(self, name):
                host = system.get_host_func(self.shell)

                # First check whether this name appears in the current directory.
                # (avoids stat calls on unknown files.)
                if name in host.listdir():
                    # When this file does not exist, return
                    try:
                        s = host.stat(name)
                        if (system.files_only and not s.is_file):
                            return
                        if (system.directories_only and not s.is_dir):
                            return
                    except IOError: # stat on non-existing file.
                        return
                    finally:
                        return ChildHandler(self.shell, name)

                # Root, current and parent directory.
                if name in ('/', '..', '.') and not system.files_only:
                    return ChildHandler(self.shell, name)

        return MainHandler


class Clear(SCPHandler):
    """ Clear window.  """
    is_leaf = True
    handler_type = BuiltinType()

    def __call__(self):
        sys.stdout.write('\033[2J\033[0;0H')
        sys.stdout.flush()

class Exit(SCPHandler):
    """ Quit the SFTP shell. """
    is_leaf = True
    handler_type = BuiltinType()

    def __call__(self):
        self.shell.exit()


class Connect(SCPHandler):
    is_leaf = True
    handler_type = RemoteType()

    def __call__(self): # XXX: code duplication of deployer/shell.py
        initial_input = "cd '%s'\n" % esc1(self.shell.host.getcwd())
        self.shell.host.start_interactive_shell(self.shell.pty, initial_input=initial_input)


class Lconnect(SCPHandler):
    is_leaf = True
    handler_type = LocalType()

    def __call__(self): # XXX: code duplication of deployer/shell.py
        initial_input = "cd '%s'\n" % esc1(self.shell.localhost.getcwd())
        self.shell.localhost.start_interactive_shell(self.shell.pty, initial_input=initial_input)


class display(AutocompleteSystem):
    """ Display remote file. """
    files_only = True

    def run(self, shell, host, path):
        console = Console(shell.pty)

        with host.open(path, 'r') as f:
            def reader():
                while True:
                    line = f.readline()
                    if line:
                        yield line.rstrip('\n')
                    else:
                        return # EOF

            console.lesspipe(reader())

class Pwd(SCPHandler):
    """ Display remote working directory. """
    is_leaf = True
    handler_type = RemoteType()

    def __call__(self):
        print self.shell.host.getcwd()



class cd(AutocompleteSystem):
    """ Change directory. """
    directories_only = True

    def run(self, shell, host, path):
        host.host_context._chdir(path)
        print host.getcwd()
        if not self.is_local:
            host.fill_cache(shell.pty)


def make_ls_handler(handler_type_, get_host_func):
    """ Make a function that does a directory listing """
    class Ls(SCPHandler):
        is_leaf = True
        handler_type = handler_type_()

        def __call__(self):
            host = get_host_func(self.shell)
            files = host.listdir()

            def iterator():
                for f in files:
                    if host.stat(f).is_dir:
                        yield colored(f, DirectoryType.color), len(f)
                    else:
                        yield f, len(f)

            console = Console(self.shell.pty)
            console.lesspipe(console.in_columns(iterator()))
    return Ls

ls = make_ls_handler(RemoteType, lambda shell: shell.host)
lls = make_ls_handler(LocalType, lambda shell: shell.localhost)


class Lpwd(SCPHandler):
    """ Print local working directory. """
    handler_type = LocalType()
    is_leaf = True

    def __call__(self):
        print self.shell.localhost.getcwd()


class display(AutocompleteSystem):
    """ Display local file. """
    files_only = True

    def run(self, shell, host, path):
        console = Console(shell.pty)

        with host.open(path, 'r') as f:
            def reader():
                while True:
                    line = f.readline()
                    if line:
                        yield line.rstrip('\n')
                    else:
                        return # EOF

            console.lesspipe(reader())

@local_handler(files_only=True)
def put(shell, filename):
    """ Upload local-path and store it on the remote machine. """
    print 'Uploading %s...', filename
    h = shell.host
    h.put_file(os.path.join(shell.localhost.getcwd(), filename),
            filename, logger=shell.logger_interface)


@remote_handler(files_only=True)
def get(shell, filename):
    """ Retrieve the remote-path and store it on the local machine """
    target = os.path.join(shell.localhost.getcwd(), filename)
    print 'Downloading %s to %s...' % (filename, target)
    h = shell.host
    h.get_file(filename, target, logger=shell.logger_interface)


@remote_handler()
def stat_handler(shell, filename):
    """ Print stat information of this file. """
    s = shell.host.stat(filename)

    print ' Is file:      %r' % s.is_file
    print ' Is directory: %r' % s.is_dir
    print
    print ' Size:         %r bytes' % s.st_size
    print
    print ' st_uid:       %r' % s.st_uid
    print ' st_gid:       %r' % s.st_gid
    print ' st_mode:      %r' % s.st_mode


@local_handler()
def lstat(shell, filename):
    """ Print stat information for this local file. """
    s =  shell.localhost.stat(filename)

    print ' Is file:      %r' % stat.S_ISREG(s.st_mode)
    print ' Is directory: %r' % stat.S_ISDIR(s.st_mode)
    print
    print ' Size:         %r bytes' % int(s.st_size)
    print
    print ' st_uid:       %r' % s.st_uid
    print ' st_gid:       %r' % s.st_gid
    print ' st_mode:      %r' % s.st_mode


@local_handler(files_only=True)
def ledit(shell, host, path):
    """ Edit file in editor. """
    host.run(shell.pty, "vim '%s'" % esc1(path))


class RootHandler(SCPHandler):
    subhandlers = {
            'clear': Clear,
            'exit': Exit,

            'ls': ls,
            'pwd': Pwd,
            'cd': cd,
            'stat': stat_handler,
            'display': display,
            'edit': edit,
            'connect': Connect,

            'lls': lls,
            'lpwd': Lpwd,
            'lcd': lcd,
            'lstat': lstat,
            'ldisplay': ldisplay,
            'ledit': ledit,
            'lconnect': Lconnect,

            'put': put,
            'get': get,
    }

    def complete_subhandlers(self, part):
        # Built-ins
        for name, h in self.subhandlers.items():
            if name.startswith(part):
                yield name, h(self.shell)

    def get_subhandler(self, name):
        if name in self.subhandlers:
            return self.subhandlers[name](self.shell)



class Shell(CLInterface):
    """
    Interactive secure copy shell.
    """
    def __init__(self, pty, host, logger_interface, clone_shell=None): # XXX: import clone_shell
        assert issubclass(host, Host)

        self.host = type('RemoteSCPHost', (CacheMixin, host), { })()
        self.host.fill_cache(pty)
        self.localhost = LocalHost()
        self.localhost.host_context._chdir(os.getcwd())
        self.logger_interface = logger_interface
        self.pty = pty
        self.root_handler = RootHandler(self)

        CLInterface.__init__(self, self.pty, RootHandler(self))

        # Caching for autocompletion (directory -> list of content.)
        self._cd_cache = { }

    @property
    def prompt(self):
        get_name = lambda p: os.path.split(p)[-1]

        return [
                    ('local:%s' % get_name(os.getcwd()), 'yellow'),
                    (' ~ ', 'cyan'),
                    ('%s:' % self.host.slug, 'yellow'),
                    (get_name(self.host.getcwd() or ''), 'yellow'),
                    (' > ', 'cyan'),
                ]
