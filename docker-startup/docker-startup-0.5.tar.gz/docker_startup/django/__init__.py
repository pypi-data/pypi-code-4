from functools import wraps

from docker_startup.base import Startup

import os

# decorators
def with_postgresql(method):
    @wraps(method)
    def dec(self, *args, **kwargs):
        _exec = getattr(self, '_exec')
        _exec(['service', 'postgresql', 'start'])
        method(self, *args, **kwargs)
        _exec(['service', 'postgresql', 'stop'])
    return dec


# helpers
def activate(prefix):
    """Activates virtualenv."""
    activate_this = os.path.join(prefix, 'bin/activate_this.py')
    if os.path.isfile(activate_this):
        execfile(activate_this, dict(__file__=activate_this))
        print('[{0}] Activated virtualenv in "{1}"'.format(
            os.environ['STARTUP_SCRIPT'], activate_this))


class DjangoStartup(Startup):
    def pre_entrypoint_hook__init__(self):
        assert bool(self.app_repo), "The `app_repo' parameter must be set."
        super(DjangoStartup, self).pre_entrypoint_hook()

    def _call_install(self):
        print('[{0}] Performing first-time setup of app environment'.format(
            os.environ['STARTUP_SCRIPT']))

        # create the directory
        if not os.path.exists(self.app_prefix):
            print('[{0}] Path "{1}" not found, creating...'.format(
                os.environ['STARTUP_SCRIPT'], self.app_prefix))
            os.makedirs(self.app_prefix)
        # something for a discussion: do we need virtualenv for probably only
        # one python app/env per container?

        # install virtualenv
        os.chdir(self.app_prefix)
        self._exec_fg(['virtualenv', '.'])
        activate(self.app_prefix)

        # clone the package
        if not os.path.exists(self.app_path):
            if ((self.app_repo.startswith('git') or
                    self.app_repo.endswith('git'))):
                self._exec_fg(['git', 'clone', self.app_repo, self.app_path])
            else:
                self._exec_fg(['hg', 'clone', self.app_repo, self.app_path])

        if not os.path.exists(self.data_volume):
            print('[{0}] Path "{1}" not found, creating...'.format(
                os.environ['STARTUP_SCRIPT'], self.data_volume))
            os.makedirs(self.data_volume)

        # install package requirements
        if os.path.exists(os.path.join(self.app_path, 'setup.py')):
            # First, try to pip install it, then fallback to a hg/git clone.
            self._exec_fg(['pip', 'install', '--editable', self.app_path])
        else:
            app_pip_reqs = os.path.join(self.app_path, 'requirements.txt')
            if os.path.exists(app_pip_reqs):
                self._exec_fg(['pip', 'install', '-r', app_pip_reqs])

        # TODO: honcho should go to dpaw_ubuntu or maybe django-swingers reqs
        self._exec_fg(['pip', 'install', 'honcho'])
        os.chdir(self.app_path)

        # deploy
        def deploy(self):
            self._exec_fg(['python', 'manage.py', 'deploy'])

        with_postgresql(deploy)(self)

    @with_postgresql
    def provision(self, db_url):
        raise NotImplementedError('TODO')

    @with_postgresql
    def _call_manage(self, args):
        os.chdir(self.app_path)
        activate(self.app_prefix)
        if args:
            self._exec_fg(['python', 'manage.py'] + args)
        else:
            self._exec_fg(['python', 'manage.py'])

    @with_postgresql
    def _call_boot(self):
        os.chdir(self.app_path)
        activate(self.app_prefix)
        # _exec_fg to see the (unbuffered) output
        self._exec_fg(['honcho', 'start'])

    @with_postgresql
    def _call_boot_shell(self):
        os.chdir(self.app_path)
        activate(self.app_prefix)
        server = self._exec_bg(['honcho', 'start'])
        self._exec_fg(['python', 'manage.py', 'shell_plus'])
