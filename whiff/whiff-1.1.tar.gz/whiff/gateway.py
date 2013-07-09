
"""
Resource gateway registration interface.

This mechanism provides a layer of security between external resources
(such as files and databases) and the whiff configuration infrastructure.

It is intended that a gateway prevents a whiff configuration template
from accessing arbitrary resources, while allowing access to specified
resources.

For example this might allow an RPC request to read and write a specific
file in the filesystem but not any other file in the filesystem.

Python code can do anything not prevented by the operating system
but it is intended that there is no way for a whiff configuration
to inject python code provided by the whiff infrastructure. If there
is a way to inject code it is a bug that must be terminated with extreme
prejudice.

Another function of the ResourceMonitor subcomponent is to cache
resources and also prevent conflicting accesses to resources by possible
multiple concurrent requests.
"""

import os
import whiffenv

class AccessDenied(ValueError):
    """
    No access to this resource is permitted.
    Do not try parent gateway.
    """

class UnknownResource(ValueError):
    """
    This gateway interface does not know how to find the resource.
    Try parent gateway if available.
    """

class NoSuchResource(KeyError):
    """
    This gateway knows how to find the resource, but it's not there.
    """

def getResourceMonitor(env):
    test = env.get(whiffenv.RESOURCES)
    if test is None:
        raise UnknownResource, "no resource monitor found in environment"
    return test

class unusableDefault:
    "object used to indicate as a default default value which should not be used"

def getResource(env, resourcePath, default=unusableDefault):
    monitor = getResourceMonitor(env)
    try:
        resource = monitor.get(resourcePath, env)
    except (NoSuchResource,UnknownResource):
        if default is unusableDefault:
            raise
        else:
            return default
    return resource

def putResource(env, resourcePath, value):
    monitor = getResourceMonitor(env)
    result = monitor.put(resourcePath, value, env)
    return result

class ResourceMonitor:
    "wrapper to monitor allocation of resource finders for a request and prevent interference by other threads"
    def __init__(self, gateway, directory="anonymous"):
        assert isinstance(gateway, ResourceGateway)
        self.gateway = gateway
        self.directory = directory
        self.prefixToFinder = TrieDict()
    def __repr__(self):
        return "ResourceMonitor" + repr((id(self), self.directory, self.gateway))
    def getFinder(self, pathlist, env):
        "get a resource finder by using the first element on the pathlist"
        #pr
        #pr "resource monitor getting", (self, pathlist)
        p2f = self.prefixToFinder
        cached = p2f.get(pathlist)
        if cached is not None:
            #pr "found cached", cached
            remainder = pathlist[1:]
            return cached
        # otherwise find the resource finder using the gateway
        (finderPath, finder, remainder) = self.gateway.getFinder(pathlist)
        # localize finder to prevent interference from other threads
        if hasattr(finder, "localize"):
            finder = finder.localize(env)
        # cache it for possible future use
        #pr "caching", finderPath, finder
        p2f.set(finderPath, finder)
        # return it
        return (finderPath, finder, remainder)
    def get(self, resourcePathList, env):
        (finderPath, finder, remainder) = self.getFinder(resourcePathList, env)
        return finder.get(remainder)
    def put(self, resourcePathList, value, env):
        (finderPath, finder, remainder) = self.getFinder(resourcePathList, env)
        return finder.put(remainder, value)

class TrieDict:
    def __init__(self):
        self.trie = {}
    def get(self, sequence):
        #pr "triedict get", (self, sequence, self.trie)
        t = tuple(sequence)
        trie = self.trie
        for i in xrange(1,len(t)+1):
            tprefix = t[:i]
            finder = None
            try:
                finder = trie.get(tprefix)
            except TypeError:
                finder = None # unhashable
            if finder is not None:
                remainder = t[i:]
                return (tprefix, finder, remainder)
        return None
    def set(self, sequencePrefix, finder):
        t = tuple(sequencePrefix)
        self.trie[t] = finder

class ResourceGateway:
    "translate paths of form [prefix, *args] to finders"
    def __init__(self, parentGateway=None, directory=None):
        self.parentGateway = parentGateway
        self.directory = directory
        self.prefixToFinder = {}
    def bind_root(self, parentGateway):
        assert self.parentGateway is None or self.parentGateway==parentGateway, "cannot re-bind resource parent "+repr((self.parentGateway, parentGateway))
        self.parentGateway = parentGateway
    def __repr__(self):
        return "ResourceGateway"+repr((id(self), self.directory, self.parentGateway, self.prefixToFinder.keys() ))
    def registerFinder(self, prefix, finder):
        if finder is None:
            raise ValueError, "finder cannot be None"
        self.prefixToFinder[prefix] = finder
    def getFinder(self, resourcePathList):
        #pr "getFinder", (resourcePathList, self)
        #pr "from", self.prefixToFinder.keys()
        prefix = resourcePathList[0]
        remainder = resourcePathList[1:]
        try:
            #pr "ResourceGateway getFinder", (self, prefix)
            finder = self.prefixToFinder[prefix]
        except KeyError:
            # try parent if available
            if self.parentGateway:
                #pr "Get failed, trying parent"
                return self.parentGateway.getFinder(resourcePathList)
            else:
                #pr "no parent: can't find resource"
                raise UnknownResource, "can't find resource "+repr(prefix)
        #pr "found finder", finder
        # if the finder is a gateway: resolve remaining path
        if isinstance(finder, ResourceGateway):
            (fprefix, ffinder, fremainder) = finder.getFinder(remainder)
            prefix = [prefix]+list(fprefix)
            return (prefix, ffinder, fremainder)
        else:
            return ([prefix], finder, remainder)

class SimplePasswordGateway(ResourceGateway):
    "translate paths of form [user, password, prefix, *args] to finders -- all users have full access"
    def __init__(self, user1, password1):
        self.userToPassword = {}
        self.innerGateway = ResourceGateway()
        self.addUser(user1, password1)
    def getFinder(self, resourcePathList):
        authPath = self.authenticatedPathList(resourcePathList)
        (finderPath, finder, remainder) = self.innerGateway.getFinder(authPath)
        fullPath = list(authPath)+list(finderPath)
        return (fullPath, finder, remainder)
    def localize(self, env):
        # since there are no possible concurrency issues just return self
        return self
    def addUser(self, user1, password1):
        self.userToPassword[user1] = password1
    def registerFinder(self, prefix, finder):
        self.innerGateway.registerFinder(prefix, finder)
    def authenticatedPathList(self, resourcePathList):
        #pr "authenticating", resourcePathList
        try:
            [user, password] = resourcePathList[:2]
        except ValueError:
            #pr resourcePathList
            raise AccessDenied, "user and password required for resource "
        if self.userToPassword.get(user)!=password:
            raise AccessDenied, "invalid user or password for resource "
        result = resourcePathList[2:]
        return result

class FileFinder:
    "simple example finder -- allow reads/writes to a file, using a password"
    def __init__(self, password, filePath, create=True):
        self.create = create
        self.password = password
        self.filePath = filePath
    def localize(self, env):
        # since there are no possible concurrency issues just return self
        return self
    def check(self, pathlist):
        if len(pathlist)!=1 or pathlist[0]!=self.password:
            raise AccessDenied, "invalid password"        
    def get(self, pathlist):
        self.check(pathlist)
        if not os.path.exists(self.filePath):
            if self.create:
                self.put(pathlist, "")
            else:
                raise ValueError, "cannot get %s: no such file" % repr(self.filePath)
        return file(self.filePath, "rb").read()
    def put(self, pathlist, value):
        self.check(pathlist)
        if not self.create and not os.path.exists(self.filePath):
            raise ValueError, "cannot set -- no such file, create flag set false "+repr(self.filePath)
        return file(self.filePath, "wb").write(value)

class FilePatternFinder:
    "example finder -- find files in relative directory matching prefixes and suffixes"
    # could be generalized to use glob or regex
    def __init__(self, baseDirectory, settable=False, creatable=False):
        self.baseDirectory = baseDirectory
        self.pairs = []
        self.settable = settable
        self.creatable = creatable
    def localize(self, env):
        # since there are no possible concurrency issues just return self
        return self
    def addMatch(self, prefix, suffix):
        "allow matches to prefix and suffix together eg prefix='/usr/aaron/data', suffix='.txt'"
        pair = (prefix,suffix)
        if pair not in self.pairs:
            self.pairs.append(pair)
    def getPath(self, resourcePathList, testExists=True):
        if len(resourcePathList)!=1:
            raise ValueError, "invalid file specification"
        filepath = resourcePathList[0]
        if filepath.find("..")>=0:
            raise AccessDenied, "'..' not permitted in filepath "+repr(filepath)
        fullpath = os.path.join(self.baseDirectory, filepath)
        if not fullpath.startswith(self.baseDirectory): # XXXX will this test always work?
            raise ValueError, "full path is not part below base directory "+repr((fullpath, self.baseDirectory))
        if testExists and not os.path.exists(fullpath):
            raise NoSuchResource, "cannot find file"
        return fullpath
    def get(self, resourcePathList):
        file_path = self.getPath(resourcePathList)
        f = file(file_path, "rb") # xxxx always binary?
        text = f.read()
        f.close()
        return text
    def put(self, resourcePathList, value):
        value = str(value)
        file_path = self.getPath(resourcePathList, testExists=not self.creatable)
        if not self.settable:
            raise AccessDenied, "writing is not allowed via this interface"
        f = file(file_path, "wb") # xxxx always binary?
        f.write(value)
        f.close()
