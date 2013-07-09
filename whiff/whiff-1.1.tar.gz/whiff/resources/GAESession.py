"""
Store session in Google App Engine
"""

import time
from whiff.resources.sessionDirectory import Session
from whiff.rdjson import jsonParse
from whiff import whiffenv

from google.appengine.ext import db

class BinaryRelation(db.Model):
    prefix = db.StringProperty()
    name = db.StringProperty()
    value = db.TextProperty()

def getMatches(prefix, name):
    matches = list(db.GqlQuery("SELECT * FROM BinaryRelation WHERE name=:1 and prefix=:2", name, prefix))
    if len(matches)>1:
        raise ValueError, "too many results for name "+repr(name)
    return matches

def storeText(prefix, name, text):
    matches = getMatches(prefix, name)
    if not matches:
        match = BinaryRelation()
    else:
        match = matches[0]
    match.prefix = prefix
    match.name = name
    match.value = text
    match.put()
    return text

def storeJson(prefix, name, value):
    json = jsonParse.format(value, False)
    return storeText(prefix, name, json)

def getText(prefix, name, default=None):
    matches = getMatches(prefix, name)
    if not matches:
        return default
    match = matches[0]
    txt = match.value
    return txt

def getJson(prefix, name, default=None):
    txt = getText(prefix, name, default=None)
    if txt is None:
        return default
    (flag, value, end) = jsonParse.parseValue(txt)
    if not flag:
        raise ValueError, "json parse failed "+repr((flag, value, end))
    if end!=len(txt):
        raise ValueError, "garbage after end of json txt "+repr(txt[end:])
    return value

def GAEProfileFinder(sessionVariable="whiff.profile.user", passwordVariable="whiff.profile.password", prefix="profile"):
    return memorySessionFinder(sessionVariable=sessionVariable, passwordVariable=passwordVariable,
                               timeout=None)

def clearSessions(prefix="session", ageLimit=24*60*60):
    earliest = time.time()-ageLimit
    earliestStart = str(earliest)
    tooOld = db.GqlQuery("SELECT * FROM BinaryRelation WHERE prefix=:1 and name<:2", prefix, earliestStart)
    count = 0
    for x in tooOld:
        x.delete()
        count+=1
    return count

class GAESessionFinder(Session):
    def __init__(self, sessionVariable="whiff.session.id", timeout=None, passwordVariable=None, prefix="session"):
        #pr "memorySessionFinder init", (sessionVariable, timeout, passwordVariable)
        self.prefix = prefix
        self.sessionVariable = sessionVariable
        self.passwordVariable = passwordVariable
        self.timeout = timeout
        self.sessionId = None
        self.sessionData = None
        self.remoteAddress = None
        
    def clone(self):
        result = GAESessionFinder(self.sessionVariable, self.timeout, self.passwordVariable, prefix=self.prefix)
        return result

    def storeData(self):
        data = self.sessionData.copy()
        data["time"] = str(time.time())
        data["id"] = self.sessionId
        storeJson(self.prefix, self.sessionId, data)

    def loadData(self):
        # XXXX eventually factor out timing logic...
        data = getJson(self.prefix, self.sessionId, None)
        #pr "testing", data
        if data is None:
            #pr "no session data found"
            return None # no such session found
        # check time stamp
        timeString = data.get("time")
        if timeString is None:
            #pr "no session timestamp found"
            return None # invalid session: no time recorded
        try:
            timestamp = float(timeString)
        except ValueError:
            #pr "bad session timestamp"
            self.invalidate()
            return None # invalid time string, bad session
        now = time.time()
        elapsed = now-timestamp
        if self.timeout and elapsed>self.timeout:
            #pr "session expired"
            self.invalidate()
            return None # expired session
        self.sessionData = data
        # update the timestamp
        data["time"] = str(now)
        #pr "session data found", self.sessionVariable, self.sessionId
        #pr "data=", data
        storeJson(self.prefix, self.sessionId, data)
        return data
    
    def invalidate(self):
        #pr "invalidating", self.sessionId
        matches = getMatches(self.prefix, self.sessionId)
        for m in matches:
            m.delete()

class GAEShadowPageFinder:
    def __init__(self, directory, pagePath=None):
        self.directory = directory
        self.pagePath = pagePath
    def localize(self, env):
        pagepath = env[whiffenv.ENTRY_POINT]
        return GAEShadowPageFinder(self.directory, pagepath)
    def get(self, pathlist):
        assert len(pathlist)==0, "no parameters expected"
        return getText(self.directory, self.pagePath, "")
    def put(self, pathlist, value):
        assert len(pathlist)==0, "no parameters expected"
        return storeText(self.directory, self.pagePath, value)


        
