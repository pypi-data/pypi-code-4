"""
Get a fresh name, for example to uniqely identify a new HTML DOM object
"""

class FreshNameFinder:
    def __init__(self, prefix="name", count=0):
        self.prefix = prefix
        self.count = count
        #pr "init FNF", id(self)
    def localize(self, env):
        #pr "localize FNF", id(self)
        return FreshNameFinder(self.prefix, self.count)
    def get(self, pathlist):
        #pr "get FNF", id(self), self.count
        prefix = self.prefix
        if pathlist:
            assert len(pathlist)==1, "expect at most one argument "+repr(pathlist)
            prefix = str(pathlist[0])
        self.count += 1
        return prefix+repr(self.count)
