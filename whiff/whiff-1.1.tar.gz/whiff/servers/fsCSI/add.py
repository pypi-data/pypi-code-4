"""
Add files matching a glob pattern to a search archive.  Usage:

% python add.py DIRECTORY_ROOT ARCHIVE_PATH GLOB_PATTERN LEXER_NAME

example:

% python add.py /export/source/trunk ~/arExport "*.jws" java

This parses java-web-services files (*.jws) under directory /export/source/trunk
as java source and adds them to the archive ~/arExport.
"""

import build
import fnmatch
import pygments.lexers
import nucular.Nucular

def add(directory_root, archive_path, glob_pattern, lexer_name, verbose=True):
    print "adding files under", directory_root, "matching", glob_pattern, "to", archive_path, "using lexer", lexer_name
    lexer = pygments.lexers.get_lexer_by_name(lexer_name)
    archive = nucular.Nucular.Nucular(archive_path)
    count = 0
    for path in build.generate_file_descendents(directory_root):
        if fnmatch.fnmatch(path, glob_pattern):
            print "found match", repr(path)
            count += 1
            entry = build.entry_for_file(path, lexer)
            if entry:
                archive.index(entry)
            if count%100==0:
                if verbose:
                    print "   ... storing at", count
                    archive.store(lazy=True)
                    archive = nucular.Nucular.Nucular(archive_path)
    print "...done adding at", count, "now aggregating"
    archive.store()
    archive.aggregateRecent(fast=False, verbose=verbose)
    print "...move transient to base"
    archive.moveTransientToBase(verbose=False)
    print "cleaning up retired files"
    archive.cleanUp()
    print "done adding files"

if __name__=="__main__":
    import sys
    try:
        [directory_root, archive_path, glob_pattern, lexer_name] = sys.argv[1:]
    except:
        print "bad arguments", sys.argv[1:]
        print __doc__
    else:
        add(directory_root, archive_path, glob_pattern, lexer_name)
    
