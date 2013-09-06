#
# Part of wpupdater package
#


def check_for_new_version():
    rt_code = False
    CURR_VERSION_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'WP_CURRENT_VERSION')
    r = urllib2.urlopen('http://wordpress.org/latest.tar.gz.md5')
    remote_md5 = r.read().strip()
    f = open(CURR_VERSION_FILE, 'r')
    local_md5 = f.read().strip()
    f.close()
    if remote_md5 != local_md5:
        rt_code = True
        f = open(CURR_VERSION_FILE, 'w+')
        f.write(remote_md5)
        f.close()
    return rt_code

class LoginException(Exception):
    def __init__(self, msg):
        self.msg = msg


def loggedin(func):
    def f(self, *args, **kwargs):
        if not self.logged_in:
            raise LoginException("Not logged in!")
        return func(self, *args, **kwargs)
    return f
