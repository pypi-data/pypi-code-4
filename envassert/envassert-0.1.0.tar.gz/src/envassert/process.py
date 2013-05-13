from __future__ import with_statement
from fabric.api import run, hide
import re

RE_SPACES = re.compile("[\s\t]+")


def is_up(name, exact=False):
    if len(process_find(name, exact)) > 0:
        return True
    else:
        return False


def is_down(name, exact=False):
    if len(process_find(name, exact)) == 0:
        return True
    else:
        return False


def process_find(name, exact=False):
    """Returns the pids of processes with the given name. If exact is `False`
    it will return the list of all processes that start with the given
    `name`."""
    is_string = isinstance(name, str) or isinstance(name, unicode)
    # NOTE: ps -A seems to be the only way to not have the grep appearing
    # as well
    with hide("everything"):
        if is_string:
            processes = run("ps -A | grep -v grep | grep {0} ; true".format(name))
        else:
            processes = run("ps -A")
    res = []
    for line in processes.split("\n"):
        if not line.strip():
            continue
        line = RE_SPACES.split(line, 3)
        # 3010 pts/1    00:00:07 gunicorn
        # PID  TTY      TIME     CMD
        # 0    1        2        3
        # We skip lines that are not like we expect them (sometimes error
        # message creep up the output)
        if len(line) < 4:
            continue
        pid, tty, time, command = line
        if is_string:
            if pid and ((exact and command == name) or (not exact and command.find(name) >= 0)):
                res.append(pid)
        elif name(line) and pid:
            res.append(pid)
    return res


def running_under_supervisor(service):
    raise NotImplementedError
    with hide("everything"):
        return run("supervisorctl status %s | grep %s && echo OK ; true" % (service, service)).endswith("OK")
