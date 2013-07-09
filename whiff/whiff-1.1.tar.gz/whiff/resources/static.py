"""
static resource: for now not writable
"""

class staticResource:
    def __init__(self, value):
        self.value = value
    def localize(self, env):
        return self
    def get(self, pathlist):
        assert not pathlist, "no parameters expected in pathlist"
        return self.value
