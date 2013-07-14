#!/usr/bin/env python2.7
# -*- conding: utf-8 -*-
from fabric.api import run, local, sudo, env
import os.path
import re


COMMAND_INVALUD = -1
COMMENT_LINE = 0
COMMAND_RUN = 1
COMMAND_SUDO = 2
COMMAND_SUDO_WITH_USER = 3
COMMAND_LOCAL = 4

COMMENT_LINE_TYPE = '^\s*?#'
COMMAND_RUN_TYPE = '^\s*?\$\s*?(.*?)$'
COMMAND_SUDO_TYPE = '^\s*?sudo\$\s*?(.*?)$'
COMMAND_SUDO_WITH_USER_TYPE = '^\s*?sudo@([\w-]*?)\$\s*?(.*?)$'
COMMAND_LOCAL_TYPE = '^\s*?local\$\s*?(.*?)$'


def _switch_run(local_mode):
    """ docstring for _switch_run
    """
    if local_mode:
        return local
    else:
        return run


def _execute_by_sudo(cmd, user=None):
    if user:
        results = sudo(cmd, user=user)
    else:
        results = sudo(cmd)
    return results


def execute_naked_procedure(filename, local_mode=0):
    """ filename is your procedure
        $ cat sample.lst
        date
        hostname
        $ fab execute_naked_procedure:sample.lst
    """

    naked = NakedCommand(local_mode=1)

    run = _switch_run(local_mode)
    pat = re.compile("\r$|\n$|\r\n$")
    path_to_proc = os.path.abspath(filename)
    with open(path_to_proc, "r") as f:
        procedures = []
        for ln in f.readlines():
            procedures.append(naked.judge_command(ln))
        for parsed_cmd in procedures:
            naked.execute_command(parsed_cmd)
            #print parsed_cmd


class NakedCommand(object):
    """NakedCommand class
    """
    def __init__(self, local_mode=0):
        super(NakedCommand, self).__init__()
        if local_mode:
            self.run = local

    def judge_command(self, cmd):
        """judge command type
            return dictionary
                - command_type
                - command
                - user
        """
        parsed_cmd = dict(
            command_type=None,
            command=None,
            user=None)
        # comment line pattern
        if re.search(COMMENT_LINE_TYPE, cmd):
            parsed_cmd["command_type"] = COMMENT_LINE
            return parsed_cmd

        # local command line
        if re.search(COMMAND_LOCAL_TYPE, cmd):
            command = re.search(COMMAND_LOCAL_TYPE, cmd).group(1)
            parsed_cmd["command_type"] = COMMAND_LOCAL
            parsed_cmd["command"] = command
            return parsed_cmd

        # run command line
        if re.search(COMMAND_RUN_TYPE, cmd):
            command = re.search(COMMAND_RUN_TYPE, cmd).group(1)
            parsed_cmd["command_type"] = COMMAND_RUN
            parsed_cmd["command"] = command
            return parsed_cmd

        # sudo command line
        if re.search(COMMAND_SUDO_TYPE, cmd):
            command = re.search(COMMAND_SUDO_TYPE, cmd).group(1)
            parsed_cmd["command_type"] = COMMAND_SUDO
            parsed_cmd["command"] = command
            return parsed_cmd

        # sudo command line
        if re.search(COMMAND_SUDO_WITH_USER_TYPE, cmd):
            exec_user = re.search(COMMAND_SUDO_WITH_USER_TYPE, cmd).group(1)
            command = re.search(COMMAND_SUDO_WITH_USER_TYPE, cmd).group(2)
            parsed_cmd["command_type"] = COMMAND_SUDO
            parsed_cmd["command"] = command
            parsed_cmd["user"] = exec_user
            return parsed_cmd

        return COMMAND_INVALUD

    def execute_command(self, cmd):
        """judge command type
            return dictionary
                - command_type
                - command
                - user(option)
        """
        # comment line pattern
        command_type = cmd["command_type"]
        exec_cmd = cmd["command"]
        exec_user = cmd["user"]
        results = ''
        if command_type == COMMENT_LINE:
            pass
        elif command_type == COMMAND_RUN:
            results = run(exec_cmd)
        elif command_type == COMMAND_SUDO:
            results = sudo(exec_cmd)
        elif command_type == COMMAND_SUDO_WITH_USER:
            results = sudo(exec_cmd, user=exec_user)
        elif command_type == COMMAND_LOCAL:
            results = local(exec_cmd)
        else:
            pass
        return results


class DSLManager(object):
    """ DSLManager: support to expand your work procedure
        not imprement

        - open dsl
        - import dsl
        - recursive import
    """
    def __init__(self, *args, **kwargs):
        super(DSLManager, self).__init__()


if __name__ == '__main__':
    env.use_ssh_config = True
    execute_naked_procedure("test/sample.dsl", 1)
