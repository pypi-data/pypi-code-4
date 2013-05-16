from __future__ import with_statement
from fabric.api import run, hide, env


def exists(location):
    with hide("everything"):
        return run('test -e "%s" && echo OK ; true' % (location)).endswith("OK")


def is_file(location):
    with hide("everything"):
        return run("test -f '%s' && echo OK ; true" % (location)).endswith("OK")


def is_dir(location):
    with hide("everything"):
        return run("test -d '%s' && echo OK ; true" % (location)).endswith("OK")


def is_link(location):
    with hide("everything"):
        return run("test -L '%s' && echo OK ; true" % (location)).endswith("OK")


def dir_exists(location):
    with hide("everything"):
        return run('test -d "%s" && echo OK ; true' % (location)).endswith("OK")


def has_line(location, line):
    try:
        text = open(location).read()
    except:
        return False
    if text.find(line) > 0:
        return True
    else:
        return False


def owner_is(location, name):
    with hide("everything"):
        if env.platform_family == "freebsd":
            return run('stat -f %%Su %s | grep "^%s$" && echo OK ; true' % (location, name)).endswith("OK")
        else:
            return run('stat -c %%U %s | grep "^%s$" && echo OK ; true' % (location, name)).endswith("OK")


def mode_is(location, name):
    with hide("everything"):
        if env.platform_family == "freebsd":
            return run('stat -f %%Op %s | cut -c 4-6 | grep "^%s$" && echo OK ; true' % (location, name)).endswith("OK")
        else:
            return run('stat -c %%a %s | grep "^%s$" && echo OK ; true' % (location, name)).endswith("OK")


def group_is(location, name):
    with hide("everything"):
        if env.platform_family == "freebsd":
            return run('stat -f %%Sg %s | grep "^%s$" && echo OK ; true' % (location, name)).endswith("OK")
        else:
            return run('stat -c %%G %s | grep "^%s$" && echo OK ; true' % (location, name)).endswith("OK")
