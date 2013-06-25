import os
from fabric.api import task, env
from djeploy import set_env


@task
def set_fab_option(**kwargs):
    ''' Set a fabric option (env) from the CLI
    '''
    for k, v in kwargs.items():
        setattr(env, k, v)


@task
def set_option(**kwargs):
    ''' Set a djeploy option from the CLI
    '''
    return set_env(**kwargs)
