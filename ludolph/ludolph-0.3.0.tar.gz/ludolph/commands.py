"""
Copyright (C) 2012-13 Erigones s.r.o.
This file is part of Ludolph.

See the file LICENSE for copying permission.
"""
import subprocess

def available_commands():
    available_commands = ['who', 'uptime']
    return available_commands

#def enabled_commands():

def execute_command(cmd):
    if cmd in available_commands():
        return True, str(subprocess.check_output(cmd))
    else:
        return False, 'Command '+ cmd +' was not recognized.'
