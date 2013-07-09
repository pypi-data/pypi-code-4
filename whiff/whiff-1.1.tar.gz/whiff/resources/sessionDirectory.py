"""
Store sessions in directory.

Obtaining a session conforms to behaviour required by middleware/session:

prefix+["id", oldId] --> oldId if the old Id is valid
prefix+["id", oldId] --> newId if the old Id is invalid or timed out, etc.
prefix+["new", id, password] --> True iff a new session with id/pw can be established, else False

Values addressed by

prefix+["item", key]

To invalidate the session set the resource path

prefix+["valid", false]

The current session id is extracted from an environment entry (default "whiff.session.id").
if passwordVariable is not None then the passwordVariable entry in the session data
must be compatible with the passwordVariable entry in the environment or the session will
be set invalid.

The keycountLimit and keysizeLimit are provided to prevent an intruder
from building an arbitrarily large session object.  If these values are exceeded
the session is treated as 'timed out/invalid' and a new session is created.
"""

from whiff import gateway
import time
import os
from whiff.rdjson import jsonParse
from whiff import whiffenv

class Session:
    sessionVariable = passwordVariable = None
    remoteAddress = None
    
    def localize(self, env):
        sessionId = env.get(self.sessionVariable)
        password = env.get(self.passwordVariable)
        if sessionId is None:
            sessionId = self.sessionId
            password = self.passwordVariable
        result = self.clone()
        result.sessionId = sessionId
        result.password = password
        result.remoteAddress = env.get("REMOTE_ADDR", "NO_REMOTE_ADDRESS")
        #pr self, "localized with", (self.sessionVariable, sessionId, password)
        return result

    def clone(self):
        raise ValueError, "define at subclass"

    def invalidate(self):
        raise ValueError, "define at subclass"

    def establishNewSession(self, sessionId=None):
        "this may be overloaded to return False on failure"
        # check password if defined
        if self.passwordVariable is not None:
            if self.password is None:
                return None # cannot establish new session if password is not set
        remote = self.remoteAddress
        if remote is None:
            raise ValueError, "no remote address"
        if sessionId is None:
            sessionId = str(time.time())+"."+remote
        self.sessionData = {}
        self.sessionId = sessionId
        self.storeDataAndPassword()
        #pr "establishing new sessionId", self.sessionId
        return self.sessionId

    def storeDataAndPassword(self):
        if self.passwordVariable is not None:
            password = self.password
            self.sessionData[self.passwordVariable] = password
        return self.storeData()

    def storeData(self):
        raise ValueError, "storeData must be defined at subclass"

    def loadDataAndCheck(self):
        data = self.loadData()
        # check the password if present
        if data is not None and self.passwordVariable is not None:
            password = self.password
            datapassword = data.get(self.passwordVariable)
            #pr "CHECKING PASSWORDS", (password, datapassword)
            if password is None:
                return None # no password sent
            if datapassword is None:
                raise ValueError, "did not find any password in stored data"
            if datapassword!=password:
                return None # password match failure (maybe should be an error?)
        # otherwise return the data
        return data

    def loadData(self):
        raise ValueError, "loadData must be defined at subclass"
    
    def validId(self, identity, password):
        "for possible overloading: sanity check id and pw"
        if password:
            password = password.strip()
        return (identity.strip(), password)
    
    def get(self, pathlist):
        #pr "session get for id", self.sessionVariable, self.sessionId, pathlist
        indicator = pathlist[0]
        if indicator=="id":
            # find a session id
            #pr "attempting load for session", pathlist
            assert len(pathlist)==2, "expect ['id', oldvalue] for id get"
            oldvalue = pathlist[1]
            # try to load session data using the old value as the session id
            self.sessionId = oldvalue
            data = self.loadDataAndCheck()
            if data is not None:
                # session ok
                #pr "got data", data
                return self.sessionId
            # if password is required, do not automatically establish a new session
            if self.passwordVariable is not None:
                #pr "failed to get id: cannot allocate new session if password is required"
                return False # failed to establish session.
            # otherwise need to make a new session:
            #pr "load data failed"
            self.sessionId = self.establishNewSession()
            #pr "reset session id", self.sessionId
            return self.sessionId
        elif indicator=="new":
            assert len(pathlist)==3, "expect ['new', id, pw] for get new session"
            [indicator, identity, password] = pathlist
            (identity, password) =  self.validId(identity,password)
            if not identity or not password:
                return False
            # if data exists, then the id is in use
            self.sessionId = identity
            self.password = password
            data = self.loadData() # (don't check data)
            if data is not None:
                self.sessionId = self.password = self.sessionData = None
                return False # cannot overwrite existing session
            # otherwise establish a new session
            self.sessionId = self.establishNewSession(identity)
            #pr "now storing new", self.sessionId, self.sessionVariable
            self.storeDataAndPassword()
            #pr "done storing new"
            return self.sessionId
        elif indicator=="item":
            # get an item
            #pr "getting", pathlist
            assert len(pathlist)==2, "expect ['item', key] for item get"
            data = self.sessionData
            if data is None:
                data = self.loadDataAndCheck()
            key = pathlist[1]
            assert data is not None, "no established and valid session data available"
            # if key ends with "_unreadable" then do not permit reads
            assert not key.endswith("_unreadable"), "unreadable key can only be set and tested, not read"
            result = data.get(key, "") # convention: missing defaults to empty string
            #pr "from data", data
            #pr "for", key
            #pr "found", result
            return result
        elif indicator=="testEqual":
            # test for equality
            assert len(pathlist)==3, "expect ['testEqual', key, value] for equality test"
            data = self.sessionData
            if data is None:
                data = self.loadDataAndCheck()
            key = pathlist[1]
            value = pathlist[2]
            assert data is not None, "no established and valid session data available"
            result = (data.get(key)==value)
            return result            
        else:
            raise ValueError, "unknown indicator "+repr(indicator)

    def put(self, pathlist, value):
        #pr "session put", (self.sessionVariable, self.sessionId, pathlist, value)
        indicator = pathlist[0]
        if indicator=="valid":
            # invalidate the session if directed
            assert len(pathlist)==2, "expect ['valid', flag] for validity put"
            flag = pathlist[0]
            if not flag:
                self.invalidate()
        elif indicator=="item":
            #pr "putting", pathlist
            assert len(pathlist)==2, "expect ['item', key] for item put"
            data = self.sessionData
            if data is None:
                data = self.loadDataAndCheck()
            #pr "putting into data", data
            key = pathlist[1]
            assert self.sessionData is not None, "no established and valid session data available"
            self.sessionData[key] = value
            #pr "now storing data for put", pathlist
            self.storeDataAndPassword()
        else:
            raise ValueError, "don't know how to put for indicator: "+repr(indicator)

def directoryProfileFinder(directory,
                           sessionVariable="whiff.profile.user", passwordVariable="whiff.profile.password"):
    return directorySessionFinder(directory,
                                  sessionVariable=sessionVariable, passwordVariable=passwordVariable,
                                  timeout=None)

class directorySessionFinder(Session):
    def __init__(self, directory, sessionVariable="whiff.session.id",
                 timeout=None, keycountLimit=1000, keysizeLimit=1000, passwordVariable=None,
                 filemod=int("777", 8)):
        self.directory = directory
        self.sessionVariable = sessionVariable
        self.timeout = timeout
        self.keycountLimit = keycountLimit
        self.keysizeLimit = keysizeLimit
        self.sessionId = None
        self.sessionData = None
        self.remoteAddress = None
        self.passwordVariable = passwordVariable
        self.password = None
        self.filemod = filemod

    def clone(self):
        return directorySessionFinder(self.directory, self.sessionVariable,
                                      self.timeout, self.keycountLimit, self.keysizeLimit, self.passwordVariable)
    
    def storeData(self):
        data = self.sessionData.copy()
        data["time"] = str(time.time())
        data["id"] = self.sessionId
        filepath = self.filePath()
        filetext = jsonParse.format(data)
        f = file(filepath, "w")
        f.write(filetext)
        f.close()
        if self.filemod:
            try:
                os.chmod(filepath, self.filemod)
            except:
                pass
        
    def loadData(self):
        "return successfully loaded data or None"
        if not self.sessionId:
            return None # no session id, no session
        filepath = self.filePath()
        if not os.path.exists(filepath):
            return None # cannot load: no such file
        f = file(filepath)
        filetext = f.read()
        f.close()
        (flag, data, cursor) = jsonParse.parseValue(filetext)
        if not flag:
            return None # parse failure: bad session (?)
        # check the data
        if len(data)>self.keycountLimit:
            return None # too many keys: invalid session
        for (name, value) in data.items():
            if len(name+str(value))>self.keysizeLimit:
                return None # entry too large: invalid session
        # check the timeout using file access time
        timestamp = os.path.getatime(filepath)
        elapsed = time.time()-timestamp
        if elapsed<0 or self.timeout and elapsed>self.timeout:
            return None # session timed out
        self.sessionData = data
        return data
    
    def filePath(self):
        filename = self.sessionId+".session"
        filepath = os.path.join(self.directory, filename)
        return filepath

    def validId(self, identity, password):
        if "/" in identity:
            return (None, None)
        if password:
            password = password.strip()
        return (identity.strip(), password)
        
    def invalidate(self):
        filepath = self.filepath()
        renamed = filepath+".invalid"
        try:
            os.rename(filepath, renamed)
        except OSError:
            pass
        
