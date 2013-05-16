from __future__ import with_statement
from fabric.api import run, env, hide
import inspect

def installed(package):
    func = inspect.stack()[0][3] + '_' + env.get("platform_family", 'rhel')
    return eval(func)(package)

### rhel
def installed_rhel(package):
    with hide("everything"):
        status = run("yum list installed %s ; true" % package)
    if status.find("No matching Packages") != -1 or status.find(package) == -1:
        return False
    else:
        return True


### debian
def installed_debian(package):
    if not isinstance(package, basestring):
        package = " ".join(package)
    with hide("everything"):
        status = run("dpkg-query -W -f='${Status} ' %s ; true" % package)
    if ('No packages found' in status) or ('not-installed' in status) or ("installed" not in status):
        return False
    else:
        return True


### gentoo
def installed_gentoo(package):
    raise NotImplementedError
#    with hide("everything"):
#        return run("/usr/bin/eix %s --installed ; echo OK ; true " % package).endswith("OK")

### arch
def installed_arch(package):
    if not isinstance(package, basestring):
        package = " ".join(package)
    with hide("everything"):
        status = run("pacman -Q %s ; true" % package)
    if ('was not found' in status):
        return False
    else:
        return True


### freebsd
def installed_freebsd(package):
    with hide("everything"):
        return run("pkg_info -aI | grep %s ; echo OK ; true " % package).endswith("OK")
