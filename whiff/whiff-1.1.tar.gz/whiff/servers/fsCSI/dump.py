
"""
Usage (1 argument):

% python dump.py ARCHIVE_PATH

Dump file names for files analysed in ARCHIVE_PATH.

Usage (2 argument):

% python dump.py ARCHIVE_PATH PATH_FRAGMENT PATH_FRAGMENT ...

Dump the lexical analysis stored in ARCHIVE_PATH for
the file at FILE_PATH.
"""

import find
import sys
import os
import nucular.Nucular

def dump_file_names(archive_path):
    print "   ... dumping file paths archived in", repr(archive_path)
    archive_path = os.path.abspath(os.path.expanduser(archive_path))
    archive = nucular.Nucular.Nucular(archive_path)
    id = archive.firstId()
    while id:
        print id
        id = archive.nextId(id)

def dump_file(archive_path, patterns, all=False):
    # search for entries matching patterns
    result = find.word_search_result(archive_path, patterns)
    filePaths = result.identities()
    print "found", len(filePaths), "files"
    if len(filePaths)<1:
        return
    count = 0
    # display the first 10 matching paths
    for path in filePaths:
        print ":: match ::", repr(path)
        count+=1
        if count>10:
            break
    if count<len(filePaths):
        print "..."
    print
    # dump lexical components
    for path in filePaths:
        entry = result.describe(path)
        print
        print ":: dumping lexical analysis for", repr(path)
        attributesAndValueLists = entry.attrDict().items()
        attributesAndValueLists.sort()
        for (attribute, valueList) in attributesAndValueLists:
            print attribute
            valueList.sort()
            for value in valueList:
                print "   ", attribute, ":",  repr(value)
        if not all:
            break # just display the first one if all==False

if __name__=="__main__":
    if len(sys.argv)==2:
        archive_path = sys.argv[1]
        dump_file_names(archive_path)
    else:
        all = False
        if "--all" in sys.argv:
            all = True
            sys.argv.remove("--all")
        archive_path = sys.argv[1]
        patterns = sys.argv[2:]
        dump_file(archive_path, patterns, all)
