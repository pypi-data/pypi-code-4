import subprocess
import os
import sys


def guess_app_name(app_repo):
    # guess app_name from git/hg url
    # e.g. https://bitbucket.org/dpaw/biodiversity-audit.git
    app_name = os.path.basename(app_repo)   # basename is a smart command :)
    if app_name.find('.') != -1:
        # possibly strip the extension (only)
        app_name = ".".join(app_name.split('.')[:-1])
    if app_name.find('@') != -1:
        # possibly strip the revision number as well
        app_name = "@".join(app_name.split('@')[:-1])
    return app_name


class Startup(object):
    """Generic startup class."""
    help_text = """Startup script.

Usage:
{STARTUP_SCRIPT} install [-d <database_url>]
{STARTUP_SCRIPT} provision [-d <database_url>]
{STARTUP_SCRIPT} show (copymounts|bindmounts) [-p <persist_dir> -i <image_name>]
{STARTUP_SCRIPT} manage [-d <database_url>] [<manage_arg>]...
{STARTUP_SCRIPT} boot [shell] [-d <database_url>] [-u <user>]
{STARTUP_SCRIPT} shell [-c <command>]

Options:
-h --help                   Show this screen.
-d --db=<database_url>      Use a custom database [default: postgres://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}]
-p --persist=<persist_dir>  Persistent directory (save state between runs) [default: `pwd`/persist]
-i --image=<image_name>     Name of Docker image (used to generate show statements) [default: default_base]
-u --user=<user>            Username to run the application process as [default: root]
-c --cmd=<command>          Command to execute [default: /bin/bash]

RUNNING:
{STARTUP_SCRIPT} is specified as the entrypoint for a Docker container.

To try:
    docker run -p {PORT}:{PORT} <image_name> boot

To develop or deploy using persistent storage:
    mkdir persist
    docker run <image_name> show copymounts -i <image_name> | sh --
    docker run <image_name> show bindmounts -i <image_name> | cat > dev.sh
    chmod +x dev.sh
    ./dev.sh boot"""


    def __init__(self,
                 app_prefix=os.environ.get('APP_PREFIX'),
                 app_path=os.environ.get('APP_PATH'),
                 app_repo=os.environ.get('APP_REPO'),
                 app_port=os.environ.get('APP_PORT', '8080'),
                 app_name=os.environ.get('APP_NAME'),
                 app_volume=os.environ.get('APP_VOLUME'),
                 data_volume=os.environ.get('DATA_VOLUME'),
                 *args, **kwargs):
        if 'container' not in os.environ:
            print('Sorry chum, it looks like you\'re not calling this script '
                  'from inside a Docker container!')
            print('Perhaps you really meant to type "docker build ." instead')
            exit(-1)

        # Force unbuffered output (here rather than globally)
        sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

        # for honcho/heroku and the help_text :)
        self.app_port = app_port
        os.environ['PORT'] = self.app_port


        if ((len(sys.argv) > 1 and
             sys.argv[1] == os.environ.get("STARTUP_SCRIPT"))):
            # allow to do
            # # sudo docker run <this> boot ...
            # as well as
            # # sudo docker run <this> startup.py boot ...
            del sys.argv[1]

        from docopt import docopt
        self.arguments = docopt(self.help_text.format(**os.environ))

        self.app_repo = app_repo    # can be empty here (e.g. confluence)
        self.app_name = app_name or guess_app_name(self.app_repo)
        # sensible defaults
        self.app_prefix = app_prefix or os.path.join('/opt', self.app_name)
        self.app_path = app_path or os.path.join(self.app_prefix, "src")
        self.app_volume = app_volume or self.app_path
        self.data_volume = data_volume or os.path.join(self.app_path, "media")

        os.environ['USER'] = self.arguments['--user']    # for honcho

        self.mounts = [x for x in (
            os.environ['DB_VOLUME'],
            self.app_volume,
            self.data_volume,
        ) if os.path.exists(x)]

        self.image_name = self.arguments['--image']
        self.persist_dir = self.arguments['--persist']

        os.environ['DATABASE_URL'] = self.arguments['--db']
        os.environ['PYTHONUNBUFFERED'] = 'x'

        #print(self.arguments)
        #print(os.environ)

        self.pre_entrypoint_hook()  # to modify self before the task is exec'd

        # figure out what to do
        if self.arguments['install']:
            self._call_install()
        elif self.arguments['show']:
            if self.arguments['bindmounts']:
                self._call_show_bindmounts()
            elif self.arguments['copymounts']:
                self._call_show_copymounts()
        elif self.arguments['manage']:
            self._call_manage(self.arguments['<manage_arg>'])
        elif self.arguments['boot']:
            if self.arguments['shell']:
                self._call_boot_shell()
            else:
                self._call_boot()
        elif self.arguments['shell']:
            self._call_shell([self.arguments['--cmd']])
        elif self.arguments['provision']:
            self._call_provision(self.arguments['--db'])
        else:
            print('noop')

        self.post_entrypoint_hook()  # post execution hook

    def pre_entrypoint_hook(self):
        pass

    def post_entrypoint_hook(self):
        pass

    # raw exec stuff
    def _exec(self, argv):
        print('[{0}] Running "{1}"...'.format(os.environ['STARTUP_SCRIPT'],
                                              ' '.join(argv)))
        proc = subprocess.Popen(argv, stdout=subprocess.PIPE)
        for line in proc.stdout.readlines():
            print(line)
        proc.wait()
        if (proc.returncode != 0):
            print('[{0}] "{1}" returned {2}, exiting!'.format(
                os.environ['STARTUP_SCRIPT'], ' '.join(argv), proc.returncode))
            exit(proc.returncode)

    def _exec_bg(self, argv):
        print('[{0}] Starting background process "{1}"...'.format(
            os.environ['STARTUP_SCRIPT'], ' '.join(argv)))
        proc = subprocess.Popen(argv, stdout=subprocess.PIPE)
        return proc

    def _exec_fg(self, argv):
        print('[{0}] Starting foreground process "{1}"...'.format(
            os.environ['STARTUP_SCRIPT'], ' '.join(argv)))
        returncode = os.system(' '.join(argv))
        if (returncode != 0):
            print('[{0}] "{1}" returned {2}, exiting!'.format(
                os.environ['STARTUP_SCRIPT'], ' '.join(argv), returncode))
            exit(returncode)

    # install methods
    def _before_install(self, *args, **kwargs):
        print('[{0}] Performing first-time setup of app environment'.format(
            os.environ['STARTUP_SCRIPT']))

        # create the app directory
        if self.app_prefix and not os.path.exists(self.app_prefix):
            print('[{0}] Path "{1}" not found, creating...'.format(
                os.environ['STARTUP_SCRIPT'], self.app_prefix))
            os.makedirs(self.app_prefix)

    def _install(self, *args, **kwargs):
        # clone the package
        if ((self.app_path and self.app_repo and
             not os.path.exists(self.app_path))):
            if ((self.app_repo.startswith('git') or
                    self.app_repo.endswith('git'))):
                self._exec_fg(['git', 'clone', self.app_repo, self.app_path])
            else:
                self._exec_fg(['hg', 'clone', self.app_repo, self.app_path])
        if os.path.exists(self.app_prefix):
            os.chdir(self.app_prefix)

    def _after_install(self, *args, **kwargs):
        # create the data directory
        # the data directory is create here rather than in ._before_install()
        # because it might prevent `package clone' if it creates a subdir of
        # self.app_path
        if self.data_volume and not os.path.exists(self.data_volume):
            print('[{0}] Path "{1}" not found, creating...'.format(
                os.environ['STARTUP_SCRIPT'], self.data_volume))
            os.makedirs(self.data_volume)

        # make the code read-only (security)
        if self.app_path and os.path.exists(self.app_path):
            self._exec_fg(['chmod', '-R', 'ugo=rx', self.app_path])

        # make the data directory rw for owner and group
        if self.data_volume:
            self._exec_fg(['chmod', '-R', 'ug=rw,o=r', self.data_volume])
            self._exec_fg(['find', self.data_volume, '-type', 'd', '-exec',
                           'chmod', 'a+x', "'{}'", '\;'])
            if os.environ.get('USER', 'root') != 'root':
                self._exec_fg(['chown', '-R',
                               ':{0}'.format(os.environ['USER']),
                               self.data_volume])

    # API calls
    def _call_install(self, *args, **kwargs):
        self._before_install()
        self._install()
        self._after_install()

    def _call_show_bindmounts(self):
        print('#!/bin/bash')
        print('docker run -p {0}:{0} -t -i '.format(self.app_port) +
              ' '.join(['-v ' + self.persist_dir + mount + ':' + mount
                        for mount in self.mounts]) +
              ' {0} "$@"'.format(self.image_name))

    def _call_show_copymounts(self):
        print('docker run -entrypoint bash -v ' + self.persist_dir + ':' +
              '/tmp/persist ' + self.image_name +
              ' -c "' + ' '.join([
              'mkdir -p ' + '/tmp/persist' + mount + '; ' +
              'cp -arvT ' + mount + ' /tmp/persist' + mount + ';'
                  for mount in self.mounts]) + '"')

    def _call_manage(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented in subclasses.')

    def _call_boot(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented in subclasses.')

    def _call_boot_shell(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented in subclasses.')

    def _call_provision(self, db_url):
        # provision db
        raise NotImplementedError('Must be implemented in subclasses.')

    def _call_shell(self, *args):
        self._exec_fg(*args)
