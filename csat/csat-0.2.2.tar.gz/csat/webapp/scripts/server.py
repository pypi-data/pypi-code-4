import argparse
import os
import sys
import pipes
import random
random = random.SystemRandom()

from twisted.python.filepath import FilePath

from csat.utils import StopAction, run_twistd, django_cmd


PIDFILE = os.environ.get('CSAT_PIDFILE', 'webserver.pid')
LOGFILE = os.environ.get('CSAT_LOGFILE', 'webserver.log')

_endpoints = {}


def runserver():
    parser = argparse.ArgumentParser('csat-webserver')
    parser.add_argument('-n', '--nodaemon', action='store_false',
                        dest='daemonize')

    StopAction.add_to_parser(parser, PIDFILE)

    parser.add_argument('envdir', default='.', nargs='?')
    parser.add_argument('endpoint', default='tcp:8000', nargs='?')

    args = parser.parse_args()

    envdir = os.path.realpath(args.envdir)

    if not os.path.exists(os.path.join(envdir, 'settings.py')):
        print (
            'The supplied directory ({}) is not a CSAT environment '
            'directory.'.format(envdir)
        )
        sys.exit(1)

    os.environ['CSAT_ENVDIR'] = envdir

    server_module = FilePath(__file__).parent().sibling('server.py')
    options = [
        '-y', server_module.path,
    ]
    if args.daemonize:
        options += [
            '--pidfile', os.path.join(envdir, PIDFILE),
            '--logfile', os.path.join(envdir, LOGFILE),
        ]
    else:
        options += [
            '--pidfile=',
            '-n',
        ]

    _endpoints['webserver'] = args.endpoint

    run_twistd(options)

settings_template = """
SECRET_KEY = '%s'

#GITHUB_OAUTH = [
#    '<client_id>',
#    '<secret>'
#]

#ALLOWED_HOSTS = []

ACQUISITION_SERVER = {
    'public': {
        'port': 7002,
    },
    'private': {
        'host': 'localhost',
        'port': 7001,
    },
}
"""


def init():
    parser = argparse.ArgumentParser('csat-init')
    parser.add_argument('envdir')

    args = parser.parse_args()

    envdir = FilePath(os.path.realpath(args.envdir))

    if envdir.exists():
        print 'The supplied environment directory already exists.'
        sys.exit(1)

    print 'Creating directory structure...'
    try:
        envdir.makedirs()
    except OSError:
        print 'Could not create the environment directory.'
        sys.exit(1)

    for d in ['graphs', 'media', 'logs']:
        envdir.child(d).makedirs()

    print 'Generating settings file...'
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    secret_key = ''.join([random.choice(chars) for i in range(50)])
    settings = settings_template.strip() % secret_key

    with envdir.child('settings.py').open('w') as fh:
        fh.write(settings)

    print 'Preparing database...'
    try:
        django_cmd(envdir.path, ['syncdb', '--noinput', '--migrate'])
    except Exception as e:
        print e.output
        sys.exit(1)

    print 'Creating \'admin\' user (you will be asked for a password)...'
    try:
        django_cmd(envdir.path, [
            'createsuperuser',
            '--username=admin',
            '--email=admin@example.com'
        ])
    except Exception as e:
        print e.output
        sys.exit(1)

    print
    print 'Environment successfully initialized. You can now start the web'
    print 'server by issuing the following command:'
    print
    print '    csat-webserver {}'.format(pipes.quote(envdir.path))
    print


if __name__ == '__main__':
    runserver()
