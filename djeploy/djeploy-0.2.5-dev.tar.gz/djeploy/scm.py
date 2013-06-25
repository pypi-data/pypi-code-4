import os
from fabric.api import task
from djeploy import djeploy_require, set_env, get_env, command


@task
def checkout_code_repo(update=False):
    ''' Check out a specified version of a source code repo.
    '''
    opts = get_env(
        'scm_bin',
        'scm_action',
        'scm_repo_rev',
        'scm_repo_name',
        'scm_repo_location',
        'scm_clone_cmd',
        'scm_update_cmd',
    )
    scm_repo_name = opts['scm_repo_name']
    scm_repo_location = opts['scm_repo_location']
    scm_clone_cmd = opts['scm_clone_cmd']
    scm_update_cmd = opts['scm_update_cmd']

    if update:
        env_path = get_env('env_path')['env_path']
        with command.cd(os.path.join(env_path, 'current', scm_repo_name)):
            command.run(scm_update_cmd % opts)
    else:
        release_path = get_env('release_path')['release_path']
        if scm_repo_location is None:
            command.abort('You must set the "scm_repo_location" value!')

        with command.cd(release_path):
            command.run(scm_clone_cmd % opts)


@task
def update_code_repo():
    ''' Update an existing repo's code base.
    '''
    checkout_code_repo(update=True)


@task
def set_repo_revision(rev='tip'):
    ''' Set repository revision to pull. Default: tip
    '''
    return set_env(scm_repo_rev=rev)
