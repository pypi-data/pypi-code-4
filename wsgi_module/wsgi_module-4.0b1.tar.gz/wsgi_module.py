from __future__ import print_function, division

import os
import sys
import shutil
import subprocess
import optparse
import math
import signal
import threading
import atexit
import imp

try:
    import Queue as queue
except ImportError:
    import queue

import apxs_config

MODULE_NAME = 'mod_wsgi-py%s%s.so' % sys.version_info[:2]

def where():
    return os.path.join(os.path.dirname(__file__), MODULE_NAME)

def find_program(names, default=None, paths=[]):
    for name in names:
        for path in os.environ['PATH'].split(':') + paths:
            program = os.path.join(path, name)
            if os.path.exists(program):
                return program
    return default

def get_apxs_config(query, apxs=None):
    if apxs is None:
        apxs = find_program(['apxs2', 'apxs'], 'apxs', ['/usr/sbin'])

    p = subprocess.Popen([apxs, '-q', query],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return out.strip()

APACHE_GENERAL_CONFIG = """
LoadModule version_module '%(LIBEXECDIR)s/mod_version.so'

ServerName %(HOST)s
ServerRoot '%(WORKDIR)s'
ErrorLog '%(LOGDIR)s/errors_log'
PidFile '%(WORKDIR)s/httpd.pid'

Listen %(HOST)s:%(PORT)s

LogLevel info

<IfVersion < 2.4>
LockFile '%(WORKDIR)s/accept.lock'
</IfVersion>

<IfVersion >= 2.4>
LoadModule mpm_event_module '%(LIBEXECDIR)s/mod_mpm_event.so'
LoadModule access_compat_module '%(LIBEXECDIR)s/mod_access_compat.so'
LoadModule unixd_module '%(LIBEXECDIR)s/mod_unixd.so'
LoadModule authn_core_module '%(LIBEXECDIR)s/mod_authn_core.so'
LoadModule authz_core_module '%(LIBEXECDIR)s/mod_authz_core.so'
</IfVersion>

LoadModule authz_host_module '%(LIBEXECDIR)s/mod_authz_host.so'
LoadModule mime_module '%(LIBEXECDIR)s/mod_mime.so'
LoadModule rewrite_module '%(LIBEXECDIR)s/mod_rewrite.so'
LoadModule alias_module '%(LIBEXECDIR)s/mod_alias.so'
LoadModule wsgi_module '%(MODULE)s'

<IfDefine SERVER_STATUS>
LoadModule status_module '%(LIBEXECDIR)s/mod_status.so'
</IfDefine>

<IfVersion < 2.4>
DefaultType text/plain
</IfVersion>

TypesConfig '%(MIMETYPES)s'

HostnameLookups Off
MaxMemFree 64
Timeout 30

<Directory />
    AllowOverride None
    Order deny,allow
    Deny from all
</Directory>

WSGIPythonHome '%(SYSPREFIX)s'
WSGIRestrictEmbedded On
WSGISocketPrefix %(WORKDIR)s/wsgi
WSGIDaemonProcess %(HOST)s:%(PORT)s display-name='%(PROCNAME)s' \
   home='%(CHDIR)s' %(PROCESSES-OPTION)s %(THREADS-OPTION)s
WSGICallableObject '%(APPLICATION)s'
WSGIPassAuthorization On

<IfDefine SERVER_STATUS>
<Location /server-status>
    SetHandler server-status
    Order deny,allow
    Deny from all
    Allow from localhost
</Location>
</IfDefine>
"""

APACHE_KEEPALIVE_ON_CONFIG = """
KeepAlive On
KeepAliveTimeout %(KEEPALIVETIMEOUT)s
"""

APACHE_KEEPALIVE_OFF_CONFIG = """
KeepAlive Off
"""

def generate_apache_general_config(fp, values):
    print(APACHE_GENERAL_CONFIG % values, file=fp)

    if values['KEEPALIVE']:
        print(APACHE_KEEPALIVE_ON_CONFIG % values, file=fp)
    else:
        print(APACHE_KEEPALIVE_OFF_CONFIG % values, file=fp)

APACHE_MPM_PREFORK_CONFIG = """
<IfModule mpm_prefork_module>
ServerLimit %(SERVERLIMIT)s
StartServers %(STARTSERVERS)s
MaxClients %(MAXCLIENTS)s
MinSpareServers %(MINSPARESERVERS)s
MaxSpareServers %(MAXSPARESERVERS)s
MaxRequestsPerChild 0
</IfModule>
"""

def generate_apache_mpm_prefork_config(fp, values):
    processes = int(values['PROCESSES'])
    threads = int(values['THREADS'])

    values = {}

    max_clients = int(1.25*processes*threads)
    server_limit = max_clients
    start_servers = max(1, int(0.1*max_clients))
    min_spare_servers = start_servers
    max_spare_servers = max(1, int(0.4*max_clients))

    values['SERVERLIMIT'] = server_limit
    values['STARTSERVERS'] = start_servers
    values['MAXCLIENTS'] = max_clients
    values['MINSPARESERVERS'] = min_spare_servers
    values['MAXSPARESERVERS'] = max_spare_servers

    print(APACHE_MPM_PREFORK_CONFIG % values, file=fp)

APACHE_MPM_WORKER_CONFIG = """
<IfModule mpm_worker_module>
ServerLimit %(SERVERLIMIT)s
ThreadLimit %(THREADLIMIT)s
StartServers %(STARTSERVERS)s
MaxClients %(MAXCLIENTS)s
MinSpareThreads %(MINSPARETHREADS)s
MaxSpareThreads %(MAXSPARETHREADS)s
ThreadsPerChild %(THREADSPERCHILD)s
MaxRequestsPerChild 0
ThreadStackSize 262144
</IfModule>

<IfModule mpm_event_module>
ServerLimit %(SERVERLIMIT)s
ThreadLimit %(THREADLIMIT)s
StartServers %(STARTSERVERS)s
MaxClients %(MAXCLIENTS)s
MinSpareThreads %(MINSPARETHREADS)s
MaxSpareThreads %(MAXSPARETHREADS)s
ThreadsPerChild %(THREADSPERCHILD)s
MaxRequestsPerChild 0
ThreadStackSize 262144
</IfModule>
"""

def generate_apache_mpm_worker_config(fp, values):
    processes = int(values['PROCESSES'])
    threads = int(values['THREADS'])

    values = {}

    max_clients = int(1.25*processes*threads)
    threads_per_child = int(min(max_clients, 25))
    thread_limit = threads_per_child

    count = max_clients/threads_per_child
    server_limit = int(math.floor(count))
    if server_limit != count:
        server_limit += 1

    max_clients = server_limit*threads_per_child

    start_servers = max(1, int(0.1*server_limit))
    min_spare_threads = max(threads_per_child,
            int(0.2*server_limit)*threads_per_child)
    max_spare_threads = max(threads_per_child,
            int(0.4*server_limit)*threads_per_child)

    values['SERVERLIMIT'] = server_limit
    values['THREADLIMIT'] = thread_limit
    values['STARTSERVERS'] = start_servers
    values['MAXCLIENTS'] = max_clients
    values['MINSPARETHREADS'] = min_spare_threads
    values['MAXSPARETHREADS'] = max_spare_threads
    values['THREADSPERCHILD'] = threads_per_child

    print(APACHE_MPM_WORKER_CONFIG % values, file=fp)

APACHE_APPLICATION_CONFIG = """
DocumentRoot '%(HTDOCS)s'

<Directory '%(WORKDIR)s'>
<Files handler.wsgi>
    Order allow,deny
    Allow from all
</Files>
</Directory>

<Directory '%(HTDOCS)s'>
    RewriteEngine On
    RewriteCond %%{REQUEST_FILENAME} !-f
<IfDefine SERVER_STATUS>
    RewriteCond %%{REQUEST_URI} !/server-status
</IfDefine>
    RewriteRule .* - [H=wsgi-handler]
    Order allow,deny
    Allow from all
</Directory>

<Directory '%(SCRIPT_DIR)s'>
<Files '%(SCRIPT_NAME)s'>
    Order allow,deny
    Allow from all
</Files>
</Directory>

WSGIHandlerScript wsgi-handler '%(WORKDIR)s/handler.wsgi' \
    process-group='%(HOST)s:%(PORT)s' application-group=%%{GLOBAL}
WSGIImportScript '%(WORKDIR)s/handler.wsgi' \
    process-group='%(HOST)s:%(PORT)s' application-group=%%{GLOBAL}
"""

def generate_apache_application_config(fp, values):
    print(APACHE_APPLICATION_CONFIG % values, file=fp)

APACHE_ALIAS_DIRECTORY_CONFIG = """
Alias '%(MOUNT)s' '%(DIRECTORY)s'

<Directory '%(DIRECTORY)s'>
    Order allow,deny
    Allow from all
</Directory>
"""

APACHE_ALIAS_FILE_CONFIG = """
Alias '%(MOUNT)s' '%(DIRECTORY)s/%(FILE)s'

<Directory '%(DIRECTORY)s'>
<Files '%(FILE)s'>
    Order allow,deny
    Allow from all
</Files>
</Directory>
"""

def generate_apache_alias_config(fp, values):
    aliases = values['ALIAS']

    for mount, target in sorted(aliases, reverse=True):
        values = {}
        values['MOUNT'] = mount
        target = os.path.abspath(target)
        if os.path.isdir(target):
            values['DIRECTORY'] = target
            print(APACHE_ALIAS_DIRECTORY_CONFIG % values, file=fp)
        else:
            values['DIRECTORY'] = os.path.dirname(target)
            values['FILE'] = os.path.basename(target)
            print(APACHE_ALIAS_FILE_CONFIG % values, file=fp)

APACHE_INCLUDE_CONFIG = """
Include '%(FILE)s'
"""

def generate_apache_include_config(fp, values):
    for path in values['INCLUDE']:
        values = {}
        values['FILE'] = path
        print(APACHE_INCLUDE_CONFIG % values, file=fp)

APACHE_WDB_CONFIG = """
WSGIDaemonProcess wdb-server display-name=%%{GROUP} threads=1
WSGIImportScript '%(WORKDIR)s/wdb-server.py' \
    process-group=wdb-server application-group=%%{GLOBAL}
"""

def generate_apache_wdb_config(fp, values):
    print(APACHE_WDB_CONFIG % values, file=fp)

_interval = 1.0
_times = {}
_files = []

_running = False
_queue = queue.Queue()
_lock = threading.Lock()

def _restart(path):
    _queue.put(True)
    prefix = 'monitor (pid=%d):' % os.getpid()
    print('%s Change detected to "%s".' % (prefix, path), file=sys.stderr)
    print('%s Triggering process restart.' % prefix, file=sys.stderr)
    os.kill(os.getpid(), signal.SIGINT)

def _modified(path):
    try:
        # If path doesn't denote a file and were previously
        # tracking it, then it has been removed or the file type
        # has changed so force a restart. If not previously
        # tracking the file then we can ignore it as probably
        # pseudo reference such as when file extracted from a
        # collection of modules contained in a zip file.

        if not os.path.isfile(path):
            return path in _times

        # Check for when file last modified.

        mtime = os.stat(path).st_mtime
        if path not in _times:
            _times[path] = mtime

        # Force restart when modification time has changed, even
        # if time now older, as that could indicate older file
        # has been restored.

        if mtime != _times[path]:
            return True
    except:
        # If any exception occured, likely that file has been
        # been removed just before stat(), so force a restart.

        return True

    return False

def _monitor():
    global _files

    while 1:
        # Check modification times on all files in sys.modules.

        for module in list(sys.modules.values()):
            if not hasattr(module, '__file__'):
                continue
            path = getattr(module, '__file__')
            if not path:
                continue
            if os.path.splitext(path)[1] in ['.pyc', '.pyo', '.pyd']:
                path = path[:-1]
            if _modified(path):
                return _restart(path)

        # Check modification times on files which have
        # specifically been registered for monitoring.

        for path in _files:
            if _modified(path):
                return _restart(path)

        # Go to sleep for specified interval.

        try:
            return _queue.get(timeout=_interval)
        except:
            pass

_thread = threading.Thread(target=_monitor)
_thread.setDaemon(True)

def _exiting():
    try:
        _queue.put(True)
    except:
        pass
    _thread.join()

def track_changes(path):
    if not path in _files:
        _files.append(path)

def start_reloader(interval=1.0):
    global _interval
    if interval < _interval:
        _interval = interval

    global _running
    _lock.acquire()
    if not _running:
        prefix = 'monitor (pid=%d):' % os.getpid()
        print('%s Starting change monitor.' % prefix, file=sys.stderr)
        _running = True
        _thread.start()
        atexit.register(_exiting)
    _lock.release()

class ApplicationHandler(object):

    def __init__(self, script, application='application', with_newrelic=False,
            with_wdb=False):
        self.script = script
        self.application = application

        self.module = imp.new_module('__wsgi__')
        self.module.__file__ = script

        with open(script, 'r') as fp:
            code = compile(fp.read(), script, 'exec', dont_inherit=True)
            exec(code, self.module.__dict__)

        self.callable_object = getattr(self.module, application)

        sys.modules['__wsgi__'] = self.module

        try:
            self.mtime = os.path.getmtime(script)
        except:
            self.mtime = None

        if with_newrelic:
            self.setup_newrelic()

        if with_wdb:
            self.setup_wdb()

    def setup_newrelic(self):
        import newrelic.agent

        config_file = os.environ.get('NEW_RELIC_CONFIG_FILE')
        environment = os.environ.get('NEW_RELIC_ENVIRONMENT')

        global_settings = newrelic.agent.global_settings()
        if global_settings.log_file is None:
            global_settings.log_file = 'stderr'

        newrelic.agent.initialize(config_file, environment)
        newrelic.agent.register_application()

        self.callable_object = newrelic.agent.WSGIApplicationWrapper(
                self.callable_object)

    def setup_wdb(self):
        from wdb.ext import WdbMiddleware
        self.callable_object = WdbMiddleware(self.callable_object)

    def reload_required(self, environ):
        try:
            mtime = os.path.getmtime(self.script)
        except:
            mtime = None

        return mtime != self.mtime

    def handle_request(self, environ, start_response):
        # Strip out the leading component due to internal redirect in
        # Apache when using web application as fallback resource.

        script_name = environ.get('SCRIPT_NAME')
        path_info = environ.get('PATH_INFO')

        environ['SCRIPT_NAME'] = ''
        environ['PATH_INFO'] = script_name + path_info

        return self.callable_object(environ, start_response)

    def __call__(self, environ, start_response):
        return self.handle_request(environ, start_response)

WSGI_HANDLER_SCRIPT = """
import wsgi_module

handler = wsgi_module.ApplicationHandler('%(script)s', '%(application)s',
        with_newrelic=%(with_newrelic)s, with_wdb=%(with_wdb)s)

reload_required = handler.reload_required
handle_request = handler.handle_request

if %(autoreload)s:
    wsgi_module.start_reloader()
"""

def generate_wsgi_handler_script(workdir, script, application,
        autoreload=False, with_newrelic=False, with_wdb=False):
    path = os.path.join(workdir, 'handler.wsgi')
    with open(path, 'w') as fp:
        print(WSGI_HANDLER_SCRIPT % dict(script=script,
                application=application, autoreload=autoreload,
                with_newrelic=with_newrelic, with_wdb=with_wdb), file=fp)

WDB_SERVER_SCRIPT = """
from wdb_server import server
from tornado.ioloop import IOLoop
from tornado.options import options
from wdb_server.sockets import handle_connection
from tornado.netutil import bind_sockets, add_accept_handler
from threading import Thread

def run_server():
    ioloop = IOLoop.instance()
    sockets = bind_sockets(options.socket_port)
    for socket in sockets:
        add_accept_handler(socket, handle_connection, ioloop)
    server.listen(options.server_port)
    ioloop.start()

thread = Thread(target=run_server)
thread.setDaemon(True)
thread.start()
"""

def generate_wdb_server_script(workdir):
    path = os.path.join(workdir, 'wdb-server.py')
    with open(path, 'w') as fp:
        print(WDB_SERVER_SCRIPT, file=fp)

def find_program(names, default=None, paths=[]):
    for name in names:
        for path in os.environ['PATH'].split(':') + paths:
            program = os.path.join(path, name)
            if os.path.exists(program):
                return program
    return default

def find_mimetypes():
    import mimetypes
    for name in mimetypes.knownfiles:
        if os.path.exists(name):
            return name
            break
    else:
        return name

def serve(script, host='localhost', port=8000, processes=None, threads=5,
        application='application', autoreload=False, htdocs=None, alias=[],
        keepalivetime=0.0, include=[], server_status=False, home=None,
        workdir=None, logdir=None, httpd=apxs_config.HTTPD,
        libexecdir=apxs_config.LIBEXECDIR, mimetypes=find_mimetypes(),
        with_newrelic=False, with_wdb=False):

    values = {}

    port = str(port)

    values['HOST'] = host
    values['PORT'] = port
    values['MODULE'] = where()

    script = os.path.abspath(script)

    values['SCRIPT_PATH'] = script
    values['SCRIPT_DIR'] = os.path.dirname(script)
    values['SCRIPT_NAME'] = os.path.basename(script)

    values['APPLICATION'] = application
    values['AUTORELOAD'] = autoreload

    values['UID'] = os.getuid()
    values['CHDIR'] = home or os.getcwd()

    values['MIMETYPES'] = mimetypes

    procname = '(wsgi:%s:%s:%s)' % (host, port, os.getuid())
    values['PROCNAME'] = procname

    if not workdir:
        workdir = '/tmp/apache-%s:%s:%s' % (host, port, os.getuid())

    try:
        os.mkdir(workdir)
    except Exception:
        pass

    if not os.path.isabs(workdir):
        workdir = os.path.abspath(workdir)

    if not htdocs:
        htdocs = os.path.join(workdir, 'htdocs')

    try:
        os.mkdir(htdocs)
    except Exception:
        pass

    if not os.path.isabs(htdocs):
        htdocs = os.path.abspath(htdocs)

    if not logdir:
        logdir = workdir

    try:
        os.mkdir(logdir)
    except Exception:
        pass

    if not os.path.isabs(logdir):
        logdir = os.path.abspath(logdir)

    values['WORKDIR'] = workdir
    values['LOGDIR'] = logdir
    values['LIBEXECDIR'] = libexecdir

    if processes is not None:
        values['PROCESSES-OPTION'] = 'processes=%s' % processes
    else:
        values['PROCESSES-OPTION'] = ''
        processes = '1'

    values['THREADS-OPTION'] = 'threads=%s' % threads

    values['PROCESSES'] = processes
    values['THREADS'] = threads

    values['MAXCLIENTS'] = str(2*int(processes)*int(threads))

    values['SYSPREFIX'] = sys.prefix

    values['HTDOCS'] = htdocs
    values['ALIAS'] = alias
    values['KEEPALIVE'] = keepalivetime != 0
    values['KEEPALIVETIMEOUT'] = keepalivetime
    values['INCLUDE'] = include

    generate_wsgi_handler_script(workdir, script, application, autoreload,
        with_newrelic, with_wdb)

    if with_wdb:
        generate_wdb_server_script(workdir)

    path = os.path.join(workdir, 'httpd.conf')
    with open(path, 'w') as fp:
        generate_apache_general_config(fp, values)
        generate_apache_mpm_prefork_config(fp, values)
        generate_apache_mpm_worker_config(fp, values)
        generate_apache_application_config(fp, values)
        generate_apache_alias_config(fp, values)
        generate_apache_include_config(fp, values)

        if with_wdb:
            generate_apache_wdb_config(fp, values)

    executable = os.environ.get('HTTPD', httpd)

    if not os.path.isabs(executable):
       executable = find_program([executable], 'httpd', ['/usr/sbin'])

    options = []

    if server_status:
        options.append('-DSERVER_STATUS')

    name = executable.ljust(len(procname))
    os.execl(executable, name, '-f', path, '-DNO_DETACH', *options)

def execute_command(func, options, args):
    kwargs = {}
    for key, value in vars(options).items():
        if value is not None:
            kwargs[key] = value

    func(*args, **kwargs)

def cmd_serve(params):
    formatter = optparse.IndentedHelpFormatter()
    formatter.set_long_opt_delimiter(' ')

    usage = '%prog serve script [options]'
    parser = optparse.OptionParser(usage=usage, formatter=formatter)

    parser.add_option('--host', default='localhost', metavar='IP-ADDRESS')
    parser.add_option('--port', default=8000, type='int', metavar='NUMBER')

    parser.add_option('--processes', type='int', metavar='NUMBER')
    parser.add_option('--threads', type='int', default=5, metavar='NUMBER')

    parser.add_option('--callable-object', dest='application',
            default='application', metavar='NAME')

    parser.add_option('--reload-on-changes', action='store_true',
            dest='autoreload', default=False)

    parser.add_option('--document-root', dest='htdocs',
            metavar='DIRECTORY-PATH')
    parser.add_option('--url-alias', action='append', nargs=2,
            dest='alias', metavar='URL-PATH FILE-PATH|DIRECTORY-PATH')
    parser.add_option('--keep-alive-timeout', type='int', default=0,
            dest='keepalivetime', metavar='SECONDS')

    parser.add_option('--server-status', action='store_true', default=False)
    parser.add_option('--include-configuration', action='append',
            dest='include', metavar='FILE-PATH')

    parser.add_option('--working-directory', dest='home',
            metavar='DIRECTORY-PATH')

    parser.add_option('--server-root', dest='workdir',
            metavar='DIRECTORY-PATH')
    parser.add_option('--log-directory', dest='logdir',
            metavar='DIRECTORY-PATH')

    parser.add_option('--httpd-executable', dest='httpd',
            default=apxs_config.HTTPD, metavar='FILE-PATH')
    parser.add_option('--modules-directory', dest='libexecdir',
            default=apxs_config.LIBEXECDIR, metavar='DIRECTORY-PATH')
    parser.add_option('--mime-types', dest='mimetypes',
            default=find_mimetypes(), metavar='FILE-PATH')

    parser.add_option('--with-newrelic', action='store_true', default=False)
    parser.add_option('--with-wdb', action='store_true', default=False)

    (options, args) = parser.parse_args(params)

    if len(args) != 1:
        parser.error('Path to WSGI script file required.')

    execute_command(serve, options, args)

def cmd_install(params):
    formatter = optparse.IndentedHelpFormatter()
    formatter.set_long_opt_delimiter(' ')

    usage = '%prog install [options]'
    parser = optparse.OptionParser(usage=usage, formatter=formatter)

    parser.add_option('--modules-directory', dest='libexecdir',
            metavar='DIRECTORY', default=apxs_config.LIBEXECDIR)

    (options, args) = parser.parse_args(params)

    if len(args) != 0:
        parser.error('Incorrect number of arguments.')

    target = os.path.abspath(os.path.join(options.libexecdir, MODULE_NAME))

    shutil.copyfile(where(), target)

    print('LoadModule wsgi_module %s' % target)

def cmd_where(params):
    formatter = optparse.IndentedHelpFormatter()
    formatter.set_long_opt_delimiter(' ')

    usage = '%prog where'
    parser = optparse.OptionParser(usage=usage, formatter=formatter)

    (options, args) = parser.parse_args(params)

    if len(args) != 0:
        parser.error('Incorrect number of arguments.')

    print(where())

main_usage="""
%prog command [params]

Commands:
    install
    serve
    where
"""

def main():
    parser = optparse.OptionParser(main_usage.strip())

    args = sys.argv[1:]

    if not args:
        parser.error('No command was specified.')

    command = args.pop(0)

    args = [os.path.expandvars(arg) for arg in args]

    if command == 'install':
        cmd_install(args)
    elif command == 'serve':
        cmd_serve(args)
    elif command == 'where':
        cmd_where(args)
    else:
        parser.error('Invalid command was specified.')

if __name__ == '__main__':
    main()
