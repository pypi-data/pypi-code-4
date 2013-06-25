'''
    Deployment fabfile for PeterSanchez.com

    Usage:
    
     # Full deploy to staging environment

       > fab space:staging deploy:full

     # Full deploy to production environment
       
       > fab space:prod deploy:full

     # Update codebase on production environment

       > fab space:prod deploy:update
'''
import os
from fabric.api import env, require
from djeploy import set_env, get_env, command
from djeploy.django import django_syncdb, django_migrate, django_collectstatic
from djeploy.ops import space, deploy
from djeploy.scm import checkout_code_repo, update_code_repo
from djeploy.system import service_command, restart_service
from djeploy.deploy import *


# deploy globals
project_name = 'pscom'

# fabric globals
env.shell = '/bin/sh -c'
env.user = 'pjs'

# djeploy options
djeploy_configs = {
    'env_path': '/home/pjs/envs/%s' % project_name,
    'scm_repo_name': project_name,
    'scm_repo_location': \
        'http://www.my-repo-location.com/hg/%s' % project_name,
}
set_env(**djeploy_configs)


def _localdev():
    'Use the local machine'
    env.hosts = ['localhost']
    opts = {
        'env_path': '/Users/pjs/envs/%s' % project_name,
        'repo_path': os.getcwd(),
        'run_type': 'local',
        'copy_base_settings_local': True,
    }
    set_env(**opts)


def _staging():
    'Use the staging environment'
    env.hosts = ['my-staging-server.com']
    set_env(run_type='staging')


def _prod():
    'Use the production environment'
    env.hosts = ['my-production-server.com']
    set_env(run_type='prod')


space_opts = {
    'space_options': {
        'local': _localdev,
        'staging': _staging,
        'prod': _prod,
        'default': lambda: command.abort('No space option was provided.'),
    },
}
set_env(**space_opts)


def _setup():
    '''
    Setup a fresh virtualenv as well as a few useful directories, then run
    a full deployment
    '''
    require('hosts', provided_by=[space])

    # Alter commands if run_type is 'local'
    command.set_cmds()

    make_release_directory()
    checkout_code_repo()
    make_virtual_environment(extra_path=project_name)
    install_requirements(cache='~/.pipcache', timeout=1)

    # Backup db before any migrations, etc.
    if not command.is_local:
        # Hide the actual running print out because it 
        # sets the password in shell via env variable PGPASSWORD
        command.set_local_settings(hide=['running',], clear_after_run=True)

        release_path = get_env('release_path')['release_path']
        postgresql_backup_db(
            project_name,
            backup_dir=release_path,
            connect_as='psanchez',
            password='my_s3cr3t_p4s5w0rd',
            host='/tmp',
            port=9999,
        )

    django_collectstatic()
    django_syncdb()
    django_migrate()

    _install_site()
    symlink_current_release()
    restart_service('apache22') # performs sanity configtest
    remove_old_releases()


def _soft_update():
    'Just update codebase. Do not do a full deploy'
    require('hosts', provided_by=[space])

    # Alter commands if run_type is 'local'
    command.set_cmds()

    checkout_code_repo(update=True)
    _touch_wsgi_handler()


deploy_opts = {
    'deploy_options': {
        'full': _setup,
        'update': _soft_update,
        'default': lambda: command.abort('No deploy option was provided.'),
    },
}
set_env(**deploy_opts)


def _install_site():
    'Add the virtualhost file to apache'
    require('hosts', provided_by=[space])
    opts = get_env('release_path')
    release_path = opts['release_path']

    if not command.is_local():
        with command.cd(release_path):
            cmd = 'cp %s/apache/%s.conf ' % (project_name, project_name) + \
                  '/usr/local/etc/apache22/Includes/'
            command.sudo(cmd)


def _touch_wsgi_handler():
    'Touch the mod_wsgi wsgi_handler.py file'
    require('hosts', provided_by=[space])
    opts = get_env('env_path')
    env_path = opts['env_path']
    wsgi_path = os.path.join(env_path, 'current', project_name, 'apache')

    with command.cd(wsgi_path):
        command.run('touch wsgi_handler.py')
