from fabric.api import *
env.ignore_virtualenv_override = True
from links_devops import (
    celery,
    debug,
    init,
    initialise as _initialise,
    manage,
    restart,
    shell,
    upgrade,
    virtualenv,
)

env.project = '{{ project }}'
env.repo = '{{ app }}'
env.app = env.repo
env.application = 'django'
env.debug_port = 8000
env.celery = False
env.memcached = True


def test(app=None):
    app = app or '{{ app }} customers instruments reports'
    local('REUSE_DB=1 ./manage.py test {} --settings={{ app }}.settings.test --with-color --with-fixture-bundling'.format(app))


def initialise(instance, *args, **kwargs):
    if instance == 'test':
        env.domains = ['{{ app }}.linkscreative.co.uk']
    elif instance == 'live':
        env.domains = ['{{ app }}-live.linkscreative.co.uk']
        
    _initialise(instance, *args, **kwargs)
    with virtualenv():
        run('mkdir -p media/uploads')
        if instance == 'test':
            manage('loaddata testdata')