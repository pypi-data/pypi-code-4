
"""
Associate to the current page (entry point) path a shadow page in a writeable directory.
Create the file if needed.
"""

from whiff import gateway
from whiff import stream
from whiff import whiffenv
import os

class ShadowPageFinder:
    def __init__(self, directory, pagePath=None):
        self.directory = directory
        self.pagePath = pagePath
        self.file = None
        
    def localize(self, env):
        pagepath = env[whiffenv.ENTRY_POINT]
        return ShadowPageFinder(self.directory, pagepath)
    
    def mangledFileName(self):
        "create a file name by mangling the pagePath"
        result = self.pagePath
        result = result.replace("/", "_")
        result = result.replace("\\", "_")
        result = result.replace(":", "_")
        return result
    
    def shadowPath(self):
        return os.path.join( self.directory, self.mangledFileName() )
    
    def get(self, pathlist):
        assert len(pathlist)==0, "no parameters expected"
        filepath = self.shadowPath()
        text = ""
        if os.path.exists(filepath):
            text = file(filepath).read()
        #return stream.myunicode(text)
        return text
    
    def put(self, pathlist, value):
        assert len(pathlist)==0, "no parameters expected"
        filepath = self.shadowPath()
        f = file(filepath, "w")
        f.write(stream.mystr(value))
