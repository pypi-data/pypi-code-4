# coding: utf-8

import subprocess as sp


def clone(uri, branch='develop', target_dir=None):
    command_line = [
        'git', 'clone',
        '-b', branch,
        uri,
    ]

    if target_dir:
        command_line.append(target_dir)

    return sp.check_call(command_line)
