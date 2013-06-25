import os
from fabric.api import task
from djeploy import djeploy_require, set_env, get_env, command


@task
def run_manage_command(cmd, *args, **kwargs):
    ''' Run manage.py syncdb
    '''
    opts = get_env(
        'release_path',
        'virtual_env_path',
        'virtual_env_dir',
        'scm_repo_name',
    )
    release_path = opts['release_path']
    virtual_env_path = opts['virtual_env_path']
    virtual_env_dir = opts['virtual_env_dir']
    scm_repo_name = opts['scm_repo_name']
    python_path = os.path.join(
        virtual_env_path,
        virtual_env_dir,
        'bin',
        'python',
    )
    manage_path = os.path.join(release_path, scm_repo_name)

    # Check for extra_path
    extra_path = kwargs.get('extra_path', None)
    if extra_path is not None:
        manage_path = os.path.join(manage_path, extra_path)

    run_cmd = '%s ./manage.py %s' % (python_path, cmd)
    if len(args):
        run_cmd += ' %s' % ' '.join(args)

    with command.cd(manage_path):
        command.run(run_cmd)


@task
def django_syncdb(*args, **kwargs):
    ''' Run manage.py syncdb
    '''
    if not args:
        args = ['--noinput']
    run_manage_command('syncdb', *args, **kwargs)


@task
def django_migrate(*args, **kwargs):
    ''' Run manage.py migrate (requires South)
    '''
    run_manage_command('migrate', *args, **kwargs)


@task
def django_collectstatic(*args, **kwargs):
    ''' Run manage.py collectstatic
    '''
    if not args:
        args = ['--noinput']
    run_manage_command('collectstatic', *args, **kwargs)
