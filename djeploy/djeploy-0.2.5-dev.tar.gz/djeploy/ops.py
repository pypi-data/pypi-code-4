from fabric.api import *
from djeploy import get_env, command


def show_valid_options(method_name, envname, keys):
    error_msg = '"%s" is an invalid %s option. ' % (envname, method_name)
    error_msg += 'Valid options are: %s' % ', '.join(keys)
    command.abort(error_msg)


@task(alias='env')
def space(envname='None'):
    ''' Specify the deploy environment. ie: space:staging
    '''
    opts = get_env('space_options')
    space_options = opts.get('space_options')
    if envname in space_options:
        func = space_options[envname]
        if not callable(func):
            command.abort('space option must be a callable function.')
        return func()
    else:
        if 'default' in space_options:
            func = space_options['default']
            if callable(func):
                return func()

    show_valid_options('space', envname, space_options.keys())


@task
def deploy(dtype='None'):
    ''' Specify the deploy type. ie, deploy:full
    '''
    opts = get_env('deploy_options')
    deploy_options = opts.get('deploy_options')
    if dtype in deploy_options:
        func = deploy_options[dtype]
        if not callable(func):
            command.abort('deploy option must be a callable function.')
        return func()
    else:
        if 'default' in deploy_options:
            func = deploy_options['default']
            if callable(func):
                return func()

    show_valid_options('deploy', dtype, deploy_options.keys())
