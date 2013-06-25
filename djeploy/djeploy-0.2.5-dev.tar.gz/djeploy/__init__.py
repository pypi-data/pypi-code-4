import sys
from djeploy.globals import set_env, djeploy_require, get_env, command


__version__ = '0.2.5-dev'

__all__ = ['set_env', 'djeploy_require', 'get_env', 'command',]


default_configs = {
    # General Settings
    'os_platform': sys.platform,
    'db_type': 'postgresql',

    # Deploy module settings
    'env_path': '/home/username/envs', # path to create release directories
    'releases_dirname': 'releases', # directory name to store the releases
    'num_releases': 5, # number of old deploys to leave on server

    # Ops module settings
    'space_options': {
        'default': lambda: command.abort('No space option was provided.'),
    },
    'deploy_options': {
        'default': lambda: command.abort('No deploy option was provided.'),
    },

    # Postgresql Options
    'postgresql_user': 'pgsql',

    # Scm module settings
    'scm_bin': 'hg', # mercurial
    'scm_action': 'clone', # hg, git use clone, svn would use 'checkout'
    'scm_repo_rev': 'stable', # repo revision to checkout
    'scm_repo_name': 'your_repo', # the name of the checked out repo
    'scm_repo_location': None, # Set to clone location, ie:
                               # http://bitbucket.org/petersanchez/djeploy
    'scm_clone_cmd': '%(scm_bin)s %(scm_action)s -r %(scm_repo_rev)s ' + \
                     '%(scm_repo_location)s %(scm_repo_name)s',
    'scm_update_cmd': '%(scm_bin)s pull -r %(scm_repo_rev)s -u',

    # System module settings
    'user_shell': '/bin/tcsh',
    'user_home_dir': '/home',
    'initd_dir': '/usr/local/etc/rc.d',
    'initd_use_pty': False,
}
set_env(**default_configs)
