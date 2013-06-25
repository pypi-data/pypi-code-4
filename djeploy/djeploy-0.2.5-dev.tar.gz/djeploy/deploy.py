import os
import time
from fabric.api import task
from djeploy import djeploy_require, set_env, get_env, command


def get_release_dir(release_dir=None):
    if release_dir is None:
        opts = get_env('env_path')
        env_path = opts['env_path']
        release_dir = os.path.join(env_path, 'releases')
    return release_dir


def get_releases_list(release_dir=None):
    ''' Returns sorted list of all current releases
    '''
    release_dir = get_release_dir(release_dir)

    with command.cd(release_dir):
        opts = {}
        if command.is_local:
            opts['capture'] = True
        releases = command.run('ls -xt', **opts)
        releases = [x.replace('/', '') for x in releases.split()]
    return sorted(releases)


@task
def fail_cleanup(release_dir=None):
    '''
    If your VERY LAST deploy failed, call this to clean up the
    mess left behind. It will only remove the most recent 
    release directory. BE CAREFUL USING THIS.
    '''
    release_dir = get_release_dir(release_dir)

    releases = get_releases_list(release_dir)
    release = releases[-1]
    with command.cd(release_dir):
        command.run('rm -rf %s' % release)


@task
def make_release_directory(release=None):
    ''' Create a new release directory.
    '''
    opts = get_env('env_path', 'releases_dirname')
    env_path = opts['env_path']
    release_dirname = opts['releases_dirname']
    if release is None:
        release = time.strftime('%Y%m%d%H%M%S')

    release_path = os.path.join(env_path, release_dirname, release)
    command.run('mkdir -p %s' % release_path)
    return set_env(release=release, release_path=release_path)


@task
def remove_old_releases(release_dir=None):
    '''
    Remove oldest releases past the ammount passed 
    in with the "num_releases" variable. Default 5.
    '''
    opts = get_env('num_releases')
    num_releases = int(opts['num_releases'])
    release_dir = get_release_dir(release_dir)

    releases = get_releases_list(release_dir)
    with command.cd(release_dir):
        if len(releases) > num_releases:
            diff = len(releases) - num_releases
            remove_releases = ' '.join(releases[:diff])
            command.run('rm -rf %s' % remove_releases)


@task
def set_num_releases(amount=5):
    ''' Set number of releases to save. Default: 5
    '''
    return set_env(num_releases=int(amount))


@task
def symlink_current_release(symlink_name='current', extra_path=None):
    ''' Symlink our current release
    '''
    opts = get_env('env_path', 'release', 'releases_dirname')
    env_path = opts['env_path']
    release = opts['release']
    release_dirname = opts['releases_dirname']

    current_dir = os.path.join(release_dirname, release)
    if extra_path is not None:
        current_dir = os.path.join(current_dir, extra_path)

    with command.cd(env_path):
        command.run('ln -nfs %s %s' % (current_dir, symlink_name))


@task
def show_versions(release_dir=None):
    ''' List all deployed versions
    '''
    release_dir = get_release_dir(release_dir)

    with command.cd(release_dir):
        print command.run('ls -xt')


@task
def rollback_version(version, release_dir=None):
    ''' Specify a specific version to be made live
    '''
    opts = get_env('env_path')
    env_path = opts['env_path']
    
    releases = get_releases_list(release_dir)
    if version not in releases:
        command.abort('Version "%s" is not a deployed release!' % version)

    with command.cd(env_path):
        command.run('ln -nfs releases/%s current' % version)


@task
def generic_rollback(release_dir=None):
    ''' Simple GENERIC rollback. Symlink to the second most recent release
    '''
    opts = get_env('env_path')
    env_path = opts['env_path']

    releases = get_releases_list(release_dir)
    release = releases[-2]
    with command.cd(env_path):
        command.run('ln -nfs releases/%s current' % release)


@task
def make_virtual_environment(extra_path=None, site_pkgs=False,
                             python=None, env_dir='env'):
    ''' Create the virtual environment
    '''
    opts = get_env('release_path')
    release_path = opts['release_path']

    if extra_path is not None:
        release_path = os.path.join(release_path, extra_path)

    if env_dir == '..':
        # Sanity check
        env_dir = '.'

    cmd = 'virtualenv '
    if not site_pkgs:
        cmd += '--no-site-packages '
    if python is not None:
        cmd += '-p %s ' % python
    cmd += env_dir

    if not command.exists(release_path):
        command.run('mkdir -p %s' % release_path)

    with command.cd(release_path):
        command.run(cmd)
        command.run('mkdir -p shared packages')

    return set_env(virtual_env_path=release_path, virtual_env_dir=env_dir)


@task
def install_requirements(req_path='./requirements.txt',
                         cache=None, timeout=None):
    ''' Install the required packages from the requirements file using pip
    '''
    opts = get_env('virtual_env_path', 'virtual_env_dir')
    virtual_env_path = opts['virtual_env_path']
    venv_dir = opts['virtual_env_dir']

    cmd = '%s/bin/pip' % venv_dir
    if timeout is not None:
        cmd += ' --timeout=%i' % int(timeout)

    cmd += ' install -r %s' % req_path
    if cache is not None:
        # If cache directory doesn't exist, pip should 
        # create it for you
        cmd += ' --download-cache=%s' % cache

    with command.cd(virtual_env_path):
        command.run(cmd)
