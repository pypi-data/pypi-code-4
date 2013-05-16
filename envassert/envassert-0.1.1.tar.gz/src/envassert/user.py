from __future__ import with_statement
from fabric.api import run, env, hide, sudo


def exists(name=None, uid=None):
    assert name != None or uid != None, "user_check: either `uid` or `name` should be given"
    assert name is None or uid is None, "user_check: `uid` and `name` both given, only one should be provided"
    if name != None:
        with hide("everything"):
            d = sudo("cat /etc/passwd | egrep '^%s:' ; true" % (name))
    elif uid != None:
        with hide("everything"):
            d = sudo("cat /etc/passwd | egrep '^.*:.*:%s:' ; true" % (uid))
    results = {}
    s = None
    if d:
        d = d.split(":")
        assert len(d) >= 7, "/etc/passwd entry is expected to have at least 7 fields, got %s in: %s" % (len(d), ":".join(d))
        results = dict(name=d[0], uid=d[2], gid=d[3], fullname=d[4], home=d[5], shell=d[6])
        with hide("everything"):
            s = sudo("cat /etc/shadow | egrep '^%s:' | awk -F':' '{print $2}'" % (results['name']))
        if s:
            results['passwd'] = s
    if results:
        return results
    else:
        return None


def is_belonging_group(user, group):
    with hide("everything"):
        return run("id %s | awk '{print $3}' | grep %s && echo OK ; true " % (user, group)).endswith("OK")
