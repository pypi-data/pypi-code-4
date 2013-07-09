"""
This resource implements temporary storage for a request
"""
from whiff import gateway

class Local:
    "store values local to this request"
    def __init__(self):
        self.store = {}
    def localize(self, env):
        return self.__class__()
    def get(self, pathlist):
        #pr "Local get", pathlist, self.store
        np = len(pathlist)
        assert np>=1, "I need a name to get from storage"
        name = pathlist[0]
        if np>1:
            default = pathlist[1]
            assert np<3, "I don't know what to do with more than 2 parameters "+repr(pathlist)
            default = self.convert(default)
            #pr "Local returning using default", (name, default)
            return self.store.get(name, default)
        #pr "Local returning using no default", (name,)
        try:
            return self.store[name]
        except KeyError:
            raise gateway.NoSuchResource, "no local resource "+repr(pathlist)
    def convert(self, value):
        "for overloading"
        return value
    def put(self, pathlist, value):
        #pr "Local put", (pathlist, value, self.store)
        assert len(pathlist)==1, "I expect a name (only) "+repr(pathlist)
        name = pathlist[0]
        value = self.convert(value)
        #pr "Local storing", (name, value)
        self.store[name] = value

class Counters(Local):
    "store counters for this request"
    def get(self, pathlist):
        #pr "Counter get", (pathlist, self.store)
        np = len(pathlist)
        assert np>=1, "I need a name to get from storage"
        name = pathlist[0]
        if np>1:
            initial = pathlist[1]
            assert np<3, "I don't know what to do with more than 2 parameters "+repr(pathlist)
            result = self.convert(self.store.get(name, initial))
        else:
            try:
                result = self.store[name]
            except KeyError:
                raise Gateway.NoSuchResource, "no initialized counter "+repr(pathlist)
            result = self.convert(result)
        self.store[name] = result + 1
        return result
    def convert(self, value):
        return int(value)
