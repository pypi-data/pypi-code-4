from __future__ import with_statement
from fabric.api import run, hide


def is_listening(port):
    with hide("everything"):
        listening = run("netstat -tunl | grep -v grep | grep ':%s ' ; true" % (port))
    if listening:
        return True
    else:
        return None
