from __future__ import with_statement
from fabric.api import run, hide


def has_entry(user, entry):
    with hide("everything"):
        return run('crontab -u %s -l | grep "%s" ; true' % (user, entry))
