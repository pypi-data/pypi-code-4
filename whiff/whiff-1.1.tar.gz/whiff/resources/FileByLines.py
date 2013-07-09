"""
Get a file by linenumbers, optimized for finding the next line.
File object and last line read are cached after first use.

This is primarily an example of a less trivial finder implementation.
Line numbers start at ZERO!!
"""
from whiff import gateway

class LineFinder:
    def __init__(self, filePath):
        self.filePath = filePath
        self.lastLine = None
        self.lastValue = None
        self.file = None
    def localize(self, env):
        "return a new finder to avoid thread interference issues"
        return LineFinder(self.filePath)
    def getFile(self):
        if self.file is not None:
            return self.file
        else:
            self.file = file(self.filePath)
            return self.file
    def get(self, pathlist):
        "get the line at the index for the last position"
        # pathlist should contain a single integer
        assert len(pathlist)==1
        lineString = pathlist[0]
        lineNumber = 0
        try:
            lineNumber = int(lineString)
        except:
            lineNumber = 0
        lastLine = self.lastLine
        theFile = self.getFile()
        result = None
        if lastLine is not None:
            if lastLine==lineNumber-1:
                # optimized path: read the next line without searching the file again...
                result = theFile.readline()
            elif self.lastResult is not None and lastLine==lineNumber:
                # optimized path, use line we just got lasttime
                result = self.lastValue
        if result is None:
            # pessimized path: start at the beginning and find the line...
            self.file.seek(0)
            result = None
            count = 0
            while count<=lineNumber:
                count += 1 # first line is at 0
                result = theFile.readline()
        if not result:
            raise gateway.NoSuchResource, "past eof"
        self.lastLine = lineNumber
        self.lastResult = result
        return result
