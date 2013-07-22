from pecan.core import Pecan as PecanApplication
from pecan_mount._compat import native_to_unicode, py3k
from pecan_mount.util import downgrade_wsgi_ux_to_1x, urljoin


class Tree(object):
    """
    A registry of Pecan applications, mounted at diverse points.

    An instance of this class may also be used as a WSGI callable
    (WSGI application object), in which case it dispatches to all
    mounted apps.

    .. attribute:: apps
    A dict of the form {script name: application}, where "script name" is
    a string declaring the URI mount point (no trailing slash), and
    "application" is an instance of pecan.Application (or an arbitrary WSGI
    callable if you happen to be using a WSGI server).
    """

    def __init__(self):
        self.apps = {}

    def mount(self, script_name="", config=None, mount_name=""):
        """Mount a new app from a root object, script_name, and config.

        script_name
            A string containing the "mount point" of the application.
            This should start with a slash, and be the path portion of the
            URL at which to mount the given root. For example, if root.index()
            will handle requests to "http://www.example.com:8080/dept/app1/",
            then the script_name argument would be "/dept/app1".

            It MUST NOT end in a slash. If the script_name refers to the
            root of the URI, it MUST be an empty string (not "/").

        config
            A file or dict containing application config.

        mount_name
            An optional name to give the mount, by default this class will
            infer the name using the script_name as a base. This is useful when
            debugging and wanting to get a better representation of what
            application is mounted where.
        """
        # Prevent a None value *always*
        script_name = script_name or ""
        mount_name = mount_name or name_from_path(script_name)

        # Prevent stepping over something already mounted
        if script_name in self.apps:
            raise AttributeError(
                "The script_name <'%s'> is already mounted for app "
                "<%s>" % (script_name, mount_name))

        # Next line both 1) strips trailing slash and 2) maps "/" -> "".
        script_name = script_name.rstrip("/")

        from pecan.core import load_app
        app = load_app(config)
        app.script_name = script_name
        app.mount_name = mount_name

        # FIXME: we need to try and merge the config here
        #if config:
            #app.merge(config)

        self.apps[script_name] = app

        return app

    def graft(self, wsgi_callable, script_name=""):
        """Mount a wsgi callable at the given script_name."""
        # Next line both 1) strips trailing slash and 2) maps "/" -> "".
        script_name = script_name.rstrip("/")
        self.apps[script_name] = wsgi_callable

    def script_name(self, path):
        """
        The script_name of the app at the given path, or None.
        """
        while True:
            if path in self.apps:
                return path

            if path == "":
                return None

            # Move one node up the tree and try again.
            path = path[:path.rfind("/")]

    def __call__(self, environ, start_response):
        # Try to look up the app using the full path.
        env1x = environ
        if environ.get(native_to_unicode('wsgi.version')) == (native_to_unicode('u'), 0):
            env1x = downgrade_wsgi_ux_to_1x(environ)
        path = urljoin(env1x.get('SCRIPT_NAME', ''),
                       env1x.get('PATH_INFO', ''))
        sn = self.script_name(path or "/")
        if sn is None:
            start_response('404 Not Found', [])
            return []

        app = self.apps[sn]

        # Correct the SCRIPT_NAME and PATH_INFO environ entries.
        # Ideally, we would update the SCRIPT_NAME here with the proper
        # value from the app that was mounted
        environ = environ.copy()
        if not py3k:
            if environ.get(native_to_unicode('wsgi.version')) == (native_to_unicode('u'), 0):
                # Python 2/WSGI u.0: all strings MUST be of type unicode
                enc = environ[native_to_unicode('wsgi.url_encoding')]
                environ[native_to_unicode('SCRIPT_NAME')] = sn.decode(enc)
                environ[native_to_unicode('PATH_INFO')] = path[len(sn.rstrip("/")):].decode(enc)
            else:
                # Python 2/WSGI 1.x: all strings MUST be of type str
                environ['SCRIPT_NAME'] = sn
                environ['PATH_INFO'] = path[len(sn.rstrip("/")):]
        else:
            if environ.get(native_to_unicode('wsgi.version')) == (native_to_unicode('u'), 0):
                # Python 3/WSGI u.0: all strings MUST be full unicode
                environ['SCRIPT_NAME'] = sn
                environ['PATH_INFO'] = path[len(sn.rstrip("/")):]
            else:
                # Python 3/WSGI 1.x: all strings MUST be ISO-8859-1 str
                environ['SCRIPT_NAME'] = sn.encode('utf-8').decode('ISO-8859-1')
                environ['PATH_INFO'] = path[len(sn.rstrip("/")):].encode('utf-8').decode('ISO-8859-1')

        return app(environ, start_response)


#
# Helpers
#
def name_from_path(path):
    """
    Given a path, try to determine the name for it, replacing
    slashes for dots.
    Alternatively, just return 'root' if nothing is passed to
    this helper.
    """
    if not path:
        return 'root'
    return path.strip('/').replace('/', '.')
