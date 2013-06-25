import os
import re
from fabric.api import env, task, put
from djeploy import djeploy_require, get_env, command


def set_environment(variable, value):
    set_env_cmd = 'setenv' if 'csh' in env.shell.split()[0] else 'export'
    extra = ' ' if set_env_cmd == 'setenv' else '='
    return '%s %s%s\'%s\' && ' % (set_env_cmd, variable, extra, value)


def get_user_home(name):
    opts = get_env('user_home_dir')
    user_home_dir = opts['user_home_dir']
    return os.path.join(user_home_dir, name)


def upload_authorized_keys(key_file, name, user_home):
    ssh_dir = os.path.join(user_home, u'.ssh')
    auth_keys_file = os.path.join(ssh_dir, u'authorized_keys')

    command.sudo(u'mkdir -p %s' % ssh_dir)
    put(key_file, auth_keys_file, use_sudo=True)

    command.sudo(u'chown -R %s %s' % (name, ssh_dir))
    command.sudo(u'chmod 0700 %s' % ssh_dir)
    command.sudo(u'chmod 0600 %s' % auth_keys_file)


def create_user_bsd(name, groups, user_shell, user_home):
    ''' Create a system user on a BSD based system.
    '''
    command.sudo(
        u'pw useradd %s -d %s -s %s %s' % (name, user_home, user_shell, groups)
    )
    command.sudo(u'pw lock %s' % name)


def remove_user_bsd(name):
    ''' Remove a system user on a BSD based system.
    '''
    command.sudo(u'rmuser -y %s' % name)


def create_user_linux(name, groups, user_shell, user_home):
    ''' Create a system user on a Linux based system.
    '''
    command.sudo(u'useradd -m %s -s %s %s' % (groups, user_shell, name))
    command.sudo(u'passwd -d %s' % name)


def remove_user_linux(name):
    ''' Remove a system user on a Linux based system.
    '''
    command.sudo(u'userdel -r %s' % name)


PLATFORM_REGEX = {
    r'^(free|net|open)bsd[0-9]$': (create_user_bsd, remove_user_bsd),
    r'^linux[0-9]$': (create_user_linux, remove_user_linux),
}


@task
def create_user(name, groups=None, key_file=None):
    ''' Create a new user account. Set groups and upload key file.
    '''
    opts = get_env('os_platform', 'user_shell')
    platform = opts['os_platform']
    user_shell = opts['user_shell']
    user_home = get_user_home(name)

    if groups is not None and not isinstance(groups, (list, tuple)):
        groups = [groups]
    groups = u'-G %s' % u','.join(groups) if groups else u''

    for pattern, (func, _) in PLATFORM_REGEX.items():
        if re.match(pattern, platform):
            func(name, groups, user_shell, user_home)
            command.sudo(
                u'mkdir -p %s && chown %s %s' % (user_home, name, user_home)
            )
            break

    if key_file:
        upload_authorized_keys(key_file, name, user_home)


@task
def remove_user(name):
    ''' Remove a system user account.
    '''
    opts = get_env('os_platform')
    platform = opts['os_platform']
    user_home = get_user_home(name)

    for pattern, (_, func) in PLATFORM_REGEX.items():
        if re.match(pattern, platform):
            func(name)
            command.sudo(u'rm -rf %s' % user_home)
            break


@task
def check_command_output(cmd, pattern, use_sudo=False, **kwargs):
    ''' Check the output of a command (cmd) using regular expression 
        defined in pattern. Pattern can be a list of several regexp 
        patterns and each one will be validated.

        If all pass, then None is returned. Otherwise, the output 
        with the unmatched pattern is given in a tuple format.
    '''
    use_command = 'sudo' if use_sudo else 'run'
    func_cmd = getattr(command, use_command)
    if not isinstance(pattern, (list, tuple)):
        pattern = [pattern]

    response = []
    output = func_cmd(cmd, **kwargs)
    for ptrn in pattern:
        if not re.search(ptrn, output):
            response.append((output, ptrn))
    return response or None


@task
def service_command(name, *commands, **kwargs):
    ''' Run an init.d command.
    '''
    opts = get_env('initd_dir', 'initd_use_pty')
    initd_dir = opts['initd_dir']
    use_pty = \
        opts['initd_use_pty'] if 'use_pty' not in kwargs else kwargs['use_pty']

    cmd_path = os.path.join(initd_dir, name)
    cmd = ' '.join(commands)

    command.sudo(u'%s %s' % (cmd_path, cmd), pty=use_pty, **kwargs)


@task
def start_service(name, **kwargs):
    ''' Start an init.d service.
    '''
    service_command(name, u'start', **kwargs)


@task
def stop_service(name, **kwargs):
    ''' Stop an init.d service.
    '''
    service_command(name, u'stop', **kwargs)


@task
def restart_service(name, **kwargs):
    ''' Restart an init.d service.
    '''
    service_command(name, u'restart', **kwargs)
