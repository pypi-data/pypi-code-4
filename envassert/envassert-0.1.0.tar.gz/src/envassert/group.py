from __future__ import with_statement
from fabric.api import run, env, hide, sudo


def is_exists(name):
    with hide("everything"):
        group_data = run("getent group | egrep '^%s:' ; true" % (name))
    if group_data:
        return True
    else:
        return None
