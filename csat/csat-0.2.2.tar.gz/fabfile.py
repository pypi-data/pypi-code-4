import os
import contextlib
import subprocess
import signal
import pipes

from fabric.api import env, sudo, cd, settings, prefix, task, local, hide
from fabric.contrib.console import confirm


env.app = {
    'user': 'csat',
    'dir': '/srv/csat',
    'envdir': 'data',
    'package': 'https://github.com/GaretJax/csat/archive/develop.zip',
    'port': 80,
}
env.local_envdir = '/Users/garetjax/Dropbox/CSAT/workspace/sources/env'
env.user = 'root'
env.hosts = [
    'stoppani-1.tic.hefr.ch',
]


def run(cmd, *args, **kwargs):
    kwargs['user'] = env.app['user']
    return sudo(cmd, *args, **kwargs)


def appenv():
    return contextlib.nested(
        cd(os.path.join(env.app['dir'], env.app['envdir'])),
        prefix('source {dir}/bin/activate'.format(**env.app)),
    )


def local_django(*cmd, **kwargs):
    environ = ['CSAT_{}={}'.format(k.upper(), v) for k, v in kwargs.iteritems()]
    environ += ['CSAT_ENVDIR={}'.format(env.local_envdir)]
    args = [
        '--pythonpath=.',
        '--settings=csat.webapp.settings',
    ]
    cmd = environ + ['django-admin.py'] + list(cmd) + args
    return local(' '.join(cmd))


def is_working_tree_clean():
    with settings(hide('everything'), warn_only=True):
        local('git update-index -q --ignore-submodules --refresh')
        unstaged = local('git diff-files --quiet --ignore-submodules --', capture=True)
        uncommitted = local('git diff-index --cached --quiet HEAD --ignore-submodules --', capture=True)
    return unstaged.succeeded and uncommitted.succeeded


@task
def install():
    """
    Install CSAT on a remote server as defined in the 'app' environment member.
    """
    with settings(warn_only=True):
        sudo('useradd --home-dir {dir} --system --shell /bin/false '
             '--create-home {user}'.format(**env.app))

    sudo('apt-get install python-virtualenv libxml2-dev libxslt-dev authbind')
    sudo('touch /etc/authbind/byport/{port}'.format(**env.app))
    sudo('chgrp {user} /etc/authbind/byport/{port}'.format(**env.app))
    sudo('chmod g+x /etc/authbind/byport/{port}'.format(**env.app))

    with cd(env.app['dir']):
        sudo('virtualenv .', user=env.app['user'])
        with prefix('source bin/activate'):
            run('pip install {package}'.format(**env.app))
            run('csat-init {envdir}'.format(**env.app))


@task
def update():
    """
    Update the app on the remote server to the latest version.
    """
    stop()
    with cd(env.app['dir']):
        with prefix('source bin/activate'):
            run('pip install -U {package}'.format(**env.app))


@task
def uninstall():
    """
    Completely remove the app from the remote server.
    """
    stop()
    sudo('userdel {user}'.format(**env.app))
    sudo('rm -rf {dir}'.format(**env.app))
    sudo('rm /etc/authbind/byport/{port}'.format(**env.app))


@task
def start():
    """
    Starts the web and the acquisition services on the remote server.
    """
    with appenv():
        run('authbind csat-webserver . tcp:{port}'.format(**env.app))
        run('csat-acquisition-server -p tcp:1500')


@task
def stop():
    """
    Stops the web and the acquisition services on the remote server.
    """
    with appenv():
        with settings(warn_only=True):
            run('csat-webserver . -s')
            run('csat-acquisition-server -s')


@task
def restart():
    """
    Restarts the web and the acquisition services on the remote server.
    """
    stop()
    start()


@task
def weblog():
    """
    Follows the web server log on the remote server.
    """
    run('tail -f {dir}/{envdir}/webserver.log'.format(**env.app))


@task
def dev():
    """
    Runs all development services.
    """
    processes = []
    for p in ['devserver', 'watch', 'livereload']:
        processes.append(subprocess.Popen(['fab', p]))

    try:
        for p in processes:
            p.wait()
    except KeyboardInterrupt:
        for p in processes:
            p.send_signal(signal.SIGINT)


@task
def devserver():
    """
    Runs the development web server.
    """
    local_django('runserver', debug=True)


@task
def watch():
    """
    Watches the assets and rebuilds when needed.
    """
    local_django('assets', 'watch', debug=True)


@task
def livereload():
    """
    Runs a livereload server to reload assets in the browser.
    """
    process = subprocess.Popen([
        'bundle', 'exec', 'guard',
        '-i',
        '-w', env.local_envdir,
        '-G', os.path.join(os.path.dirname(__file__), 'Guardfile'),
    ])
    try:
        process.wait()
    except KeyboardInterrupt:
        process.kill()


@task
def assets(clean=False):
    """
    Rebuilds all the assets for packaging.
    """
    if clean:
        from csat import webapp
        static = os.path.join(os.path.dirname(webapp.__file__), 'static')
        local('rm -rf {}'.format(static))
    local_django('collectstatic', '--noinput')
    local_django('assets', 'build')


@task
def lint():
    """
    Checks the source code using flake8.
    """
    local('flake8 --statistics --exit-zero --max-complexity=10 --benchmark '
          '--exclude=\'*/migrations/*\' csat')


@task
def release():
    """
    Create a new release and upload it to PyPI.
    """

    if not is_working_tree_clean():
        print 'Your working tree is not clean. Refusing to create a release.'
        return

    print 'Rebuilding assets to ensure everything is up to date...'
    assets()

    if not is_working_tree_clean():
        print 'Your working tree is not clean after the assets where rebuilt.'
        print 'Please commit the changes before continuing.'
        return

    # Check version
    version = local('python setup.py --version', capture=True)

    # Tag
    tag_message = 'CSAT release version {}.'.format(version)

    print '----------------------'
    print 'Proceeding will tag the release, push the repository upstream,'
    print 'and release a new version on PyPI.'
    print
    print 'Version: {}'.format(version)
    print 'Tag message: {}'.format(tag_message)
    print
    if not confirm('Continue?', default=True):
        print 'Aborting.'
        return

    local('git tag -a {} -m {}'.format(pipes.quote(version),
                                       pipes.quote(tag_message)))

    # Push
    local('git push origin master')

    # Package and upload to pypi
    local('python setup.py sdist upload')
