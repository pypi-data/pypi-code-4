from __future__ import with_statement
from fabric.api import run, env, hide
import inspect

def is_enabled(service):
    '''service enabled or not.'''

    func = inspect.stack()[0][3] + '_' + env.get("platform_family", 'rhel')
    return eval(func)(service)

def is_enabeld_rhel(service):
    return run("chkconfig --list %s | grep 3:on ; echo OK; true " % service).endswith("OK")

def is_enabled_debian(service):
    return run("ls /etc/rc3.d/ | grep %s ; echo OK; true " % service).endswith("OK")

def is_enabled_freebsd(service):
    return run("cat /etc/rc.conf /usr/local/etc/rc.conf |grep '%s_enable=\"YES\"' ; echo OK; true" % service).endswith("OK")
