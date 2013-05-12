#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import random
from fabric.api import local, cd, env, lcd, get, task, run
import shutil

try:
    from ua2.fabdep import depup, depstick, depver
    fabdep = True
except:
    fabdep = False

def _local_manage(runstring):
    with lcd(env.local_project_root):
        local('./manage.py %s' % runstring)


@task
def runserver():
    """ Run dev server in unique manner - on a port, which depends on
    project path.
    This allows to run different projects, on different paths, so
    stored passwords are not mixed up, when running multiple projects on
    same URL (e.g. http://127.0.0.1:8000/)

    If local.dev is present in /etc/hosts, it is used to start server.
    This is needed for local development purposes, so virtual
    environments (like VirtualBox) can access internal IP (usually 10.10.10.x).
    """

    summ = sum([ord(char) for char in env.local_project_root.split('/')[-2]])
    random.seed(summ)
    port = random.randrange(1024, 5000)

    server_address = '127.0.0.1'
    if os.path.exists('/etc/hosts'):
        with open('/etc/hosts') as f:
            if f.read().find('local.dev') != -1:
                server_address = 'local.dev'

    with cd(env.local_project_root):
        local('./manage.py runserver %s:%d' % (server_address,
                                               port), capture=False)


@task
def pullup():
    with cd(env.local_project_root):
        local('hg pull -uv', capture=False)


@task
def fcgi_reload():
    """ Reload production server (via kill all FCGI processes) """
    myfolder = filter(lambda x: x != '',
                      env.local_project_root.split('/'))[-1]
    fcgi_name = "%s.fcgi" % myfolder.replace('www.', '')
    pids = []
    for line in local('ps ux', capture=True).split('\n'):
        if fcgi_name in line:
            pids.append(re.split('\s+', line)[1])
    if pids:
        local('kill '+' '.join(pids))
    else:
        print 'No pids to kill: no process has started.'


@task
def collectstatic():
    _local_manage('collectstatic')

@task
def patch():
    _local_manage('patch up')


@task
def up():
    """ update project code / db """
    pullup()
    depup()
    patch()


@task
def produp():
    with cd(env.local_project_root):
        up()
        collectstatic()
        fcgi_reload()

@task
def deploy():
    with cd(env.project_root):
        run('fab produp')

@task
def dbshell():
    """ rsync static data """
    local(env.local_project_root+'manage.py dbshell', capture=False)


def pip_install(package, arg=''):
    local('source env/bin/activate && pip install %(arg)s %(package)s' % dict(
        package=package,
        arg=arg))


@task
def env_install():
    """ install project virtual environment and required packages """

    if os.path.exists(env.local_project_root+'env'):
        print "Removing previously installed environment directory"
        shutil.rmtree(env.local_project_root+'env')

    with lcd(env.local_project_root):
        local('virtualenv --no-site-packages --distribute env')

    with lcd(env.local_project_root):
        for line in open(env.local_project_root+'doc/pip-dependencies.txt'):
            package = line.strip()
            if not line:
                continue
            pip_install(package)


def _local_dumps_dir():
    d = env.local_project_root + 'sqldumps/'
    if not os.path.exists(d):
        os.mkdir(d)
    return d


@task
def get_db():
    """ Get database from production server """
    filename = run("cd {} && ./manage.py db_dump".format(env.project_root))
    get(filename, _local_dumps_dir())


@task
def reinst_db():
    """ Restore db from latest dump """
    _local_manage('db_dump --restore')
