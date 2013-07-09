"""
Interface to build and serve searches of file system trees by lexical analysis.
REQUIRES Nucular and Pygments!

Usage:
=====

    python fsCSI.py build ARCHIVE_PATH DIRECTORY_PATH
        -- build a search archive by traversing tree at DIRECTORY_PATH.  ARCHIVE_PATH must be empty.
        
    python fsCSI.py serve ARCHIVE_PATH DIRECTORY_PATH
        -- serve HTTP search interface using the archive and directory.
            entry page at http://localhost:8888/search
        
    python fsCSI.py find ARCHIVE_PATH DIRECTORY_PATH PATTERNS...
        -- find patterns in the archive.  See find.py for description of patterns.
        
    python fsCSI.py add ARCHIVE_PATH DIRECTORY_PATH GLOB_PATTERN LEXER_NAME
        -- add additional files matching glob pattern using lexer to the archive.

Example:
=======

Build the archive

    prompt% python fsCSI.py build /tmp/trunkArchive /export/source/trunk
    ... build takes 20 minutes to scan about 1 gig of files

Then use the "find" interface from the command line to find the strings mentioning "tabular"

    prompt% python fsCSI.py find /tmp/trunkArchive /export/source/trunk string:apples
    ....
    found 14 paths

Then start the single threaded search server interface

    prompt% python fsCSI.py serve /tmp/trunkArchive /export/source/trunk

Go to http://localhost:8888/search to see in interactive search form.
"""

import build
import add
import dump
import find
from whiff.middleware import displayTraceback
from whiff import resolver
from whiff.resources import nConnect
from whiff import gateway
import fsCSIroot

def getApplication(archivePath, directoryPath):
    builder = fsCSI(archivePath, directoryPath)
    return builder.application()

class fsCSI:
    def __init__(self, archivePath, directoryPath):
        self.archivePath = archivePath
        self.directoryPath = directoryPath

    def build(self, verbose=True):
        build.archive_lexical_analysis_of_descendents(self.directoryPath, self.archivePath, verbose=verbose)
        
    def add(self, glob_pattern, lexer_name):
        add.add(self.directoryPath, self.archivePath, glob_pattern, lexer_name, verbose=verbose)
        
    def find(self, searchParams):
        find.word_search(self.archivePath, searchParams)
        
    def serve(self, server="localhost", port=8888, root=fsCSIroot):
        import wsgiref.simple_server
        application = self.application(root)
        srv = wsgiref.simple_server.make_server('localhost', 8888, application)
        print "search start page at http://localhost:8888/search"
        print "serving wsgi on port 8888"
        srv.serve_forever()
        
    def application(self, root=fsCSIroot):
        app = resolver.moduleRootApplication("/", root,
                                                 exception_middleware=displayTraceback.__middleware__,
                                                 on_not_found=None, # show traceback (could comment)
                                                 )
        nucularFinder = nConnect.Connection(self.archivePath)
        fileFinder = gateway.FilePatternFinder(self.directoryPath)
        app.registerResourceFinder(prefix="index", finder=nucularFinder)
        app.registerResourceFinder(prefix="content", finder=fileFinder)
        return app

def execute(directive, archivePath, directoryPath, otherparams):
    target = fsCSI(archivePath, directoryPath)
    if directive=="build":
        if otherparams:
            raise ValueError, "no other parameters expected for build "+repr(otherparams)
        target.build()
    elif directive=="serve":
        if otherparams:
            raise ValueError, "no other parameters expected for build "+repr(otherparams)
        target.serve()
    elif directive=="find":
        target.find(otherparams)
    elif directive=="add":
        [glob_pattern, lexer_name] = otherparams
        target.add(glob_pattern, lexer_name)
    else:
        raise ValueError, "unknown directive "+repr(directive)

def main():
    import sys
    [directive, archivePath, directoryPath] = sys.argv[1:4]
    otherparams = sys.argv[4:]
    execute(directive, archivePath, directoryPath, otherparams)

if __name__=="__main__":
    main()
