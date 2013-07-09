
"""
Guarded resource protocol implementation:

A guarded resource is a resource which may not be accessible by
all requests, or which may represent different information for
different requests.

For example a online instruction application may include a
"my dropbox" resource and an "all dropboxes" resource.

Requests on behalf of a students should allow access to "my dropbox"
where the drop box is different for different students, but deny
accesses to "all dropboxes".

Requests on behalf of the instructor should allow access to
"all dropboxes" but might leave "my dropbox" undefined.

This guarded resource protocol implements resource protection
and redirection using Guard Functions and Certificates Dictionaries.

A Certificates Dictionary is an initially empty mapping of
certificate names to certificate values which provides information
about what resources a request is allowed to access.
For example a Certificate Dictionary for a request may contain a "student"
certificate mapped to the value "george56" which indicates
that when this request accesses the "my dropbox" resource the
access should be directed to the dropbox for the student "george56".

A Guard Function decides whether a request should have access
to a resource and also may change the certificates used for
a resource.  For example a guard function for a dropbox resource
may examine the parameters for a request to find what user
is accessing the request and use external data to decide whether
that user is a student or an instructor.  If the user is "george56"
the function might add a "student":"george56" entry to the
certificates for access to the dropbox resource.  On the other
hand if the guard function can't validate the user as a student
or instructor it may revoke access to the dropbox resources
completely.
"""

from whiff import gateway

class GuardedResourceFinder:
    def localize(self, env):
        # default localization attempts access with empty certificates
        return self.authorize(env, {})
    def authorize(self, env, certificates):
        """find authorized location corresponding to the resource based on the environment and the resource certificates"""
        raise ValueError, "must be defined at subclass"

class LocationFinder(GuardedResourceFinder):
    """trivially find a resource, optionally protected by guard function."""
    def __init__(self, location, guardFunction=None):
        self.location = location
        self.guardFunction = guardFunction
    def authorize(self, env, certificates):
        guardFunction = self.guardFunction
        if guardFunction is not None:
            certificates = guardFunction(certificates)
            if certificates is None:
                raise gateway.AccessDenied, "access not allowed by guard function"
        return self.location

class Location:
    def setContext(self, env, certificates):
        "record the access context"
        self.env = env
        self.certificates = certificates
    def locate(self, pathentry):
        "find subordinate path: default=none found"
        raise gateway.NoSuchResource, "subordinate paths not defined at this location: "+repr(path_entry)
    def getHere(self):
        "get value at this location (not subordinate path)"
        raise gateway.AccessDenied, "local get not defined for this location"
    def putHere(self, value):
        "put value at this location (not subordinate path)"
        raise gateway.AccessDenied, "local put not defined for this location"
    def get(self, pathlist):
        if len(pathlist)>0:
            pathentry = pathlist[0]
            pathremainder = pathlist[1:]
            subordinate_location = self.locate(pathentry)
            return subordinate_location.get(pathremainder)
        else:
            return self.getHere()
    def put(self, pathlist, value):
        if len(pathlist)>0:
            pathentry = pathlist[0]
            pathremainder = pathlist[1:]
            subordinate_location = self.locate(pathentry)
            return subordinate_location.put(pathremainder, value)
        else:
            return self.putHere(value)

def findGuarded(finder, env, certificates):
    """find an authorized or unauthorized resource using the finder"""
    if isinstance(finder, GuardedResourceFinder):
        return finder.authorize(env, certificates)
    else:
        # attempt an unprotected access
        return finder.localize(env)

class LocationFinder(GuardedResourceFinder):
    "construct location from context with no certificate testing or modification"
    def __init__(self, constructor):
        self.constructor = constructor
    def authorize(self, env, certificates):
        return self.constructor(env, certificates)

class IndexedFinder(GuardedResourceFinder):
    def authorize(self, env, certificates):
        certificates = self.guard(env, certificates)
        if certificates is not None:
            return self.indexLocation(env, certificates)
        else:
            raise gateway.AccessDenied, "access not allowed in this environment with these certificates"
    def indexLocation(self, env, certificates):
        raise ValueError, "define at subclass"
    def guard(self, env, certificates):
        "default for overloading, return (updated) resource certificates on success or None on failure"
        return certificates # default: no change

class BranchFinder(IndexedFinder):
    "branch to a fixed set of named finders"
    def __init__(self, guardFunction=None):
        self.guardFunction = guardFunction
        self.lookupDict = {}
    def branch(self, name, locationFactory, guardFunction):
        self.defineBranch(name, LocationFinder(locationFactory), guardFunction)
    def defineBranch(self, name, finder, guardFunction=None):
        self.lookupDict[name] = (guardFunction, finder)
    def indexLocation(self, env, certificates):
        guard = self.guardFunction
        if guard is not None:
            certificates = guard(env, certificates)
        if certificates is None:
            raise gateway.AccessDenied, "access to branching not allowed in this context"
        return GuardedBranchLocation(self.lookupDict, env, certificates)

class GuardedBranchLocation(Location):
    def __init__(self, lookupDict, env, certificates):
        self.lookupDict = lookupDict
        self.cache = {}
        self.setContext(env, certificates)
    def locate(self, name):
        #pr "locating name", repr(name)
        d = self.lookupDict
        c = self.cache
        if name in c:
            location = c[name]
        elif name in d:
            (guardFunction, finder) = d[name]
            certificates = self.certificates
            if guardFunction is not None:
                certificates = guardFunction(self.env, certificates)
                if certificates is None:
                    raise gateway.AccessDenied, "named access not allowed in this context "+repr(name)
            location = findGuarded(finder, self.env, certificates)
            c[location] = location
            return location
        else:
            raise gateway.NoSuchResource, "name not found "+repr(name)
    # no local putHere
    def getHere(self):
        return self.lookupDict.keys()
