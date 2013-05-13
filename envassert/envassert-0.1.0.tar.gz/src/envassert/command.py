from __future__ import with_statement
from fabric.api import run, env, hide


def is_work(command):
    with hide("everything"):
        return run("which '%s' >& /dev/null && echo OK ; true" % command).endswith("OK")
