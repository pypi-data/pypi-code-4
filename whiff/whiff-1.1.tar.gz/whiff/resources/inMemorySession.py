"""
Store session in directory.

This will only work if all access for the session are serviced
by the same Python interpreter.

Primarily for testing.
"""

import time
from sessionDirectory import Session

def memoryProfileFinder(sessionVariable="whiff.profile.user", passwordVariable="whiff.profile.password"):
    return memorySessionFinder(sessionVariable=sessionVariable, passwordVariable=passwordVariable,
                               timeout=None)

class memorySessionFinder(Session):
    def __init__(self, sessionVariable="whiff.session.id", timeout=None, passwordVariable=None):
        #pr "memorySessionFinder init", (sessionVariable, timeout, passwordVariable)
        self.sessionVariable = sessionVariable
        self.passwordVariable = passwordVariable
        self.timeout = timeout
        self.sessionId = None
        self.sessionData = None
        self.remoteAddress = None
        # THIS DICTIONARY IS SHARED BY ALL THREADS IF MULTITHREADED...
        self.SharedSessionDictionary = {}
        
    def clone(self):
        result = memorySessionFinder(self.sessionVariable, self.timeout, self.passwordVariable)
        result.SharedSessionDictionary = self.SharedSessionDictionary
        return result

    def storeData(self):
        data = self.sessionData.copy()
        data["time"] = str(time.time())
        data["id"] = self.sessionId
        #pr "storing data", (self.sessionVariable, self.sessionId, data)
        self.SharedSessionDictionary[self.sessionId] = data

    def loadData(self):
        # xxxx probably should check timestamps for all sessions and delete old ones
        #pr "loading data for", self.sessionVariable, self.sessionId
        #pr "from count", len(self.SharedSessionDictionary)
        #pr self.SharedSessionDictionary.keys()
        data = self.SharedSessionDictionary.get(self.sessionId)
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
        return data
    
    def invalidate(self):
        #pr "invalidating", self.sessionId
        try:
            del self.SharedSessionDictionary[self.sessionId]
        except KeyError:
            pass
        
