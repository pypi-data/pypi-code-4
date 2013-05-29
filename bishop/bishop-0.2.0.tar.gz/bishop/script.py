'''Provide a set of utility functions to make writing install scripts easier'''
import fnmatch
import logging
import re
import subprocess
import sys
from bishop import package

logging.basicConfig(level=logging.INFO, format='%(message)s')

changed_files = sys.argv[1:]

def sh(*args, **kwargs):
    '''Execute the given arguments as a shell script'''
    if 'capture' in kwargs and kwargs['capture']:
        f = subprocess.check_output
    else:
        f = subprocess.check_call

    if len(args) == 1 and (' ' in args[0] or '|' in args[0]):
        logging.info(args[0])
        return f(args[0], shell=True)
    else:
        logging.info(' '.join(args))
        return f(args)

def has_changed(*pats):
    '''Detect whether any files matching the given glob pattern have changed in this run'''
    for pat in pats:
        for path in changed_files:
            if fnmatch.fnmatch(path, pat):
                return True
    return False

def has_changed_re(*pats):
    '''Same as has_changed, but match using a regular expression'''
    for pat in pats:
        pat = re.compile(pat)
        for path in changed_files:
            if pat.search(path):
                return True
    return False

def update_packages():
    '''Update the package definitions'''
    package.Package().update()

def upgrade_packages():
    '''Upgrade all packages in a non-interactive way'''
    p = package.Package()
    p.update()
    p.upgrade()

def service_cmd(service, cmd):
    '''Run the given command for a service and return the result'''
    return sh('service', service, cmd)

def service_restart(service):
    '''Make sure the service is running, restarting it if necessary'''
    return service_cmd(service, 'restart')

def service_running(service):
    '''Return whether or not the service has been started'''
    try:
        output = sh('service', service, 'status', capture=True)
        if 'not running' in output or 'stop/waiting' in output:
            return False
        return True
    except:
        return False
