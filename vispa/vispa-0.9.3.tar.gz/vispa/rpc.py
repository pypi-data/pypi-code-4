import pushy
import rpyc
import os
import inspect
import sys
import logging
import random
import vispa.remote
import cherrypy
from vispa.models.user import User
from vispa.models.workspace import Workspace
import tempfile
import zipfile

logger = logging.getLogger(__name__)

_remote_files = []

def add_remote_files(files):
    for tpl in files:
        if not isinstance(tpl, tuple):
            logger.warn("add_remote_files requires a list of tuples. found %s" % str(file))
        else:
            _remote_files.append(tpl)

def directory_files(local, remote, **kwargs):
    files = kwargs.get('files', [])
    l = len(local) + 1
    for directory, _dirnames, filenames in os.walk(local):
        remote_dir = os.path.join(remote, directory[l:])
        for filename in filenames:
            if not filename.endswith('.py'):
                continue
            localfilename = os.path.join(directory, filename)
            remotefilename = os.path.join(remote_dir, filename)
            files.append((localfilename, remotefilename))
    return files

def add_directory_files(local, remote, **kwargs):
    files = directory_files(local, remote)
    _remote_files.extend(files)
    logger.info (_remote_files)

def package_files(pkg, target_path, **kwargs):
    root = os.path.dirname(inspect.getfile(pkg))
    return directory_files(root, target_path, **kwargs)

def add_package_files(pkg, target=None):
    if not target:
        target = pkg.__name__.replace('.', '/')
    files = package_files(pkg, target)
    _remote_files.extend(files)
    logger.info (_remote_files)

add_package_files(vispa.remote)

_rpyc_package_files = package_files(rpyc, "rpyc")
    
class Client(object):
    def __init__(self, target, **kwargs):
        self.__target = target
        self.__python = kwargs.get('python', 'python')
        self.__username = kwargs.get('username', None)
        if not isinstance(self.__python, (str, unicode, bytes)) or len(self.__python) == 0:
            self.__python = 'python'
        self.__server = None
        self.__tempdir = None
        self.__rpyc = None
        self.__prepared = False
        
    @staticmethod
    def scp(client, src, dst):
        ros = client.modules.os
        fsrc = os.open(src, os.O_RDONLY)
        fdst = ros.open(dst, ros.O_RDWR | ros.O_CREAT)
        while 1:
            buf = os.read(fsrc, 64*1024)
            if not buf:
                break
            ros.write(fdst, buf)

    def __copyfiles(self, client, filelists):
        zfile, zpath = tempfile.mkstemp()
        zfile = os.fdopen(zfile, "w")
        z = zipfile.ZipFile(zfile, "w")
        
        remotefolders = set()
        remotepackages = set()
        for filelist in filelists:
            for localfilename, remotefilename in filelist:
                if remotefilename.startswith("/"):
                    remotefilename = remotefilename[1:]
                logger.debug("put: '%s' -> '%s'" % (localfilename, remotefilename))
                remotefolder = os.path.dirname(remotefilename)
                remotepackagecomponents = remotefilename.split(os.sep)[:-1]
                p = ""
                for c in remotepackagecomponents:
                    p = os.path.join(p, c)
                    remotefolders.add(p)
                if os.path.basename(remotefilename) == "__init__.py":
                    remotepackages.add(remotefolder)
                z.write(localfilename, remotefilename)

        missing_packages = remotefolders.difference(remotepackages)
        for p in missing_packages:
            logger.debug("add __init__.py: %s" % (p))
            z.writestr(os.path.join(p, "__init__.py"), "")
        
        z.close()
        zfile.close()
        
        logger.info("put zip")
        rzipfilename = client.modules.os.path.join(self.__tempdir, "files.zip")
        self.scp(client, zpath, rzipfilename)   
        
        logger.info("remote: extract zip")
        rzip = client.modules.zipfile.ZipFile(rzipfilename, "r")
        rzip.extractall(self.__tempdir)
        
    def prepare_workspace(self, **kwargs):
        if self.__prepared:
            logger.debug("workspace already prepared")
            return
        
        logger.info("prepare workspace")

        client = pushy.client.PushyClient(self.__target, python=self.__python, username=self.__username)
        self.__tempdir = client.modules.tempfile.mkdtemp(prefix='vispa-rpc-')
        self.__prepared = True

        filelists = [_remote_files]              
        
        if kwargs.get('put_rpyc', True):
            logger.info("put rpyc")
            filelists.append(_rpyc_package_files)
            
        if 'put_files' in kwargs:
            filelists.append(kwargs.get('put_files'))
        
        self.__copyfiles(client, filelists)
        
        client.close()
        
    def cleanup_workspace(self):
        if not self.__prepared:
            logger.debug("workspace not prepared, no cleanup")
            return
        
        logger.debug("cleanup workspace")
        self.__prepared = False
        
        if not self.__target:
            return
        
        client = pushy.client.PushyClient(self.__target, python=self.__python, username=self.__username)
        # TODO: make sure tempdir is nothing important! 
        if self.__tempdir:
            client.modules.shutil.rmtree(self.__tempdir)
            self.__tempdir = None
            
        client.close()
        
    def open(self, **kwargs):
        self.prepare_workspace(**kwargs)
        
        (transport, address) = pushy.client.get_transport(self.__target)
        code = "import sys, os; base = '%s'; sys.path.insert(0, base); os.chdir(base); import rpyc, vispa.remote; conn = rpyc.connect_pipes(sys.stdin, sys.stdout, vispa.remote.Service, {'allow_public_attrs': True}); conn.serve_all();" % (self.__tempdir)
        logger.debug("code: %s" % (code))
        command = [self.__python, "-u", "-c", code]
        kwargs["address"] = address
        self.__server = transport.Popen(command, username=self.__username, **kwargs)
        logger.info("connect rpyc")
        try:
            self.__rpyc = rpyc.connect_pipes(self.__server.stdout, self.__server.stdin, rpyc.VoidService)
        except:
            vispa.log_exception()
            
        logger.info("connection open")
    
    def close(self):

        logger.debug("close rpyc")

        if self.__rpyc:
            self.__rpyc.close()
            self.__rpyc = None
            
        logger.debug("close transport")

        if self.__server:
            self.__server.close()
            self.__server = None
            
        self.cleanup_workspace()
        
    def stdin(self):
        return self.__server.stdin

    def stdout(self):
        return self.__server.stdout
    
    def __del__(self):
        self.close()
        
    def rpyc(self):
        return self.__rpyc
    
    def errors(self):
        for i, line in enumerate(self.__server.stderr):
            line = line.rstrip()
            logger.info("%d: %s" % (i, line))

class Pool(object):
    
    def __init__(self):
        self.__client_pool = {}
        self.__cls_pool = {}

        vispa.register_callback('user.logout', self.user_logout_callback)
    
    def __del__(self):
        logger.info("shutdown pool")
        for client in self.__client_pool.values():
            client.close()
    
    def user_logout_callback(self, user):
        for key in self.__cls_pool.keys():
            if key[0] == user.id:
                del self.__cls_pool[key]

        for key in self.__client_pool.keys():
            if key[0] == user.id:
                self.__client_pool[key].close()
                del self.__client_pool[key]

        
    def get_client(self, user, workspace, **kwargs):
        key = (user.id, workspace.id) 
        if key in self.__client_pool:
            return self.__client_pool[key]
        else:
            if workspace.host:
                hosts = workspace.host.split(',')
            else:
                hosts = ['local:']
            while len(hosts) > 0:
                try:
                    idx = random.randint(0, len(hosts) - 1)
                    target = hosts.pop(idx).strip()
                    if len(target) == 0 or target == "local:":
                        target = "local:"
                    else:
                        target = "ssh:" + target 
                    python = workspace.command if workspace.command and len(workspace.command) else None
                    logger.info("spawn remote process: '%s' using command '%s'" % (target, python))
                    client = Client(target, python=python, username=workspace.login)
                    client.open()
                    self.__client_pool[key] = client
                    return client
                except Exception:
                    vispa.log_exception()
                    logger.info("spawn remote process failed")
                    
    def get(self, _user, _workspace, classname=None, key = None, **kwargs):
        client= self.get_client(_user, _workspace, **kwargs)       
        if classname:
            _key = (_user.id, _workspace.id, classname, key)
            logger.info(str(_key))
            if _key in self.__cls_pool:
                logger.info("return pooled class %s" % classname)
                return self.__cls_pool[_key]
            cls = classname.split('.')
            module = ".".join(cls[:-1])
            name = cls[-1]
            m = client.rpyc().root.getmodule(module)
            rcls = getattr(m, name)
            if rcls:
                logger.info("return new class %s" % classname)
                instance = rcls() 
                self.__cls_pool[_key]= instance
                return instance
            else:
                logger.info("class %s not found" % classname)
                return None 
        else:
            return client.rpyc().root

    def clear(self, _user, _workspace, classname=None, key = None, **kwargs):
        _key = (_user.id, _workspace.id, classname, key)
        logger.info("clear %s" % str(_key))
        del self.__cls_pool[_key]
        
_pool = Pool();
_default_workspace = Workspace(id=0, name="default", host="local:")

def get(_user, _workspace, classname=None, key = None, **kwargs):
    db = kwargs.get('db', cherrypy.request.db if hasattr(cherrypy.request, "db") else None)
    
    if not isinstance(_user, User):
        user = User.get_by_id(db, int(_user))
    else:
        user = _user

    if not isinstance(_workspace, Workspace):
        workspace = Workspace.get_by_id(db, int(_workspace))
    elif _workspace == None:
        workspace = _default_workspace
        logger.info("use default workspace (local:)")
    else:
        workspace = _workspace
        
    return _pool.get(user, workspace, classname, key)
    
def clear(_user, _workspace, classname=None, key = None, **kwargs):
    db = kwargs.get('db', cherrypy.request.db if hasattr(cherrypy.request, "db") else None)
    
    if isinstance(_user, (int, long)):
        user = User.get_by_id(db, _user)
    else:
        user = _user

    if isinstance(_workspace, (int, long)):
        workspace = Workspace.get_by_id(db, _workspace)
    elif _workspace == None:
        workspace = _default_workspace
        logger.info("use default workspace (local:)")
    else:
        workspace = _workspace
        
    return _pool.clear(user, workspace, classname, key)
    
    
if __name__ == 'main':

    logger.root.setLevel(logging.DEBUG)
    
    # command = ['python', "-u", "-c", "import rpyc, sys; conn = rpyc.connect_pipes(sys.stdin, sys.stdout, rpyc.core.service.SlaveService()); conn.serve_all();"]
    # target = "ssh:gmueller@lx3a24"
    # python = "python"
    target = "local:"
    python = sys.executable
    files = [("extension/designer/rpc/__init__.py", "designer/rpc/__init__.py")]
    c = Client(target, python=python)
    c.open(put_files=files, put_rpyc=True)
    # c.root().namespace.os.environ['HOME']
    r = c.rpyc()
    logger.debug("print hello")
    r.execute("import os")
    print r.eval("os.environ['HOME']")
    
    import time
    r.execute("import time; s = time.time()")
    s = time.time()
    for i in range(100):
        print time.time() - s, r.eval("time.time() - s")
    
    import threading
    class TestThread(threading.Thread):
        
        def __init__(self, rpyc): 
            threading.Thread.__init__(self) 
            self.rpyc = rpyc
     
        def run(self): 
            s = time.time()
            for i in range(100):
                time.time() - s, self.rpyc.eval("time.time() - s")
    
    threads = [] 
    for i in range(10): 
        thread = TestThread(r) 
        threads += [thread] 
        thread.start() 
     
    for x in threads: 
        x.join()
    
    c.close()
    logger.info("done")
    '''
    mods = c.modules
    ros = mods.os
    remote_home = ros.environ['HOME']
    remote_vispa_temp = ros.path.join(remote_home, 'vispa-temp')
    if not ros.path.exists(remote_vispa_temp):
        ros.makedirs(remote_vispa_temp)
    c.putfile('a.py', ros.path.join(remote_vispa_temp, 'a.py'))
    c.modules.sys.path.insert(0, remote_vispa_temp)
    b = c.modules.a.b("mine")
    '''
