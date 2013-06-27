# -*- coding: utf-8 -*-
from fabric.context_managers import prefix, cd
from fabric.operations import local
from fabric.state import env
from fabric.decorators import task
from contextlib import contextmanager


env.project_root = '.'
env.target = local
env.requirements = './config/requirements.txt'
env.django_settings = 'config.settings'
env.virtualenv_root = '.env'
env.virtualenv_params = '--no-site-packages'


@contextmanager
def virtualenv():
    with cd(env.project_root):
        with prefix('source %(virtualenv_root)s/bin/activate' % env):
            yield


@task(alias='sh')
def shell(cmd):
    env.method(cmd)


@task(alias='vsh')
def virtualenv_shell(cmd):
    with virtualenv():
        shell(cmd)


# ==================================================================================================
# Python
# ==================================================================================================
@task(alias='venv-req')
def requirements():
    with virtualenv():
        shell('pip install -r %(requirements)s' % env)


@task(alias='venv-init')
def virtualenv_init():
    shell('virtualenv %(virtualenv_params)s %(virtualenv_root)s' % env)


@task(alias='git-pull')
def git_pull():
    virtualenv_shell('git pull')


@task(alias='reload')
def reload():
    virtualenv_shell('touch config/wsgi.py')


# ==================================================================================================
# Django
# ==================================================================================================
@task(alias='dj')
def django_cmd(cmd, sudo=False):
    django_cmd = 'python manage.py %s --settings %s' % (cmd, env.django_settings)
    if sudo:
        django_cmd = 'sudo ' + django_cmd
    virtualenv_shell(django_cmd)


@task(alias='dj-sync')
def django_sync():
    django_cmd('syncdb --noinput')


@task(alias='dj-static')
def django_collectstatic():
    django_cmd('collectstatic --noinput')


@task(alias='dj-admin')
def create_superuser(email='admin@admin.com'):
    django_cmd('createsuperuser --email %s' % email)


@task(alias='dj-fixture')
def fixture(name):
    django_cmd('generate_fixture %s.test_data' % name)


@task(alias='mgr')
def south_migrate(app=''):
    django_cmd('migrate %s' % app)


@task(alias='mgr-list')
def south_migrate_list():
    django_cmd('migrate --list')


@task(alias='mgr-init')
def south_migration_initial(app):
    django_cmd('schemamigration --initial %s' % app)


@task(alias='mgr-auto')
def south_migration_auto(app):
    django_cmd('schemamigration --auto %s' % app)


# ==================================================================================================
# Database
# ==================================================================================================
@task(alias='import_dump_pg')
def import_dump_postgresql(dump):
    env.method('PGPASSWORD=%(PASSWORD)s psql -U %(USER)s %(NAME)s < ' % env.postgresql + dump)
