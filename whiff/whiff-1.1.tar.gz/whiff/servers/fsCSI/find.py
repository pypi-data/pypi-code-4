"""
USAGE:

% python find.py ARCHIVE_LOCATION PATTERN1 PATTERN2 ...

Prints file paths indexed in ARCHIVE_LOCATION matching the patterns.

Patterns containing no colons are interpreted as words to search for
in all tokens.  Patterns of form TOKENTYPE:WORD are interpreted as words
to search for in only one token type

Example

% python find.py /tmp/arPy guido comment:bug

searches the archive at /tmp/arPy for files containing "guido" anywhere
and the word "bug" somewhere in a Comment token.
"""


import sys
import os
import nucular.Nucular

def word_dictionary(argumentList):
    result = {}
    for arg in argumentList:
        arg_split = arg.split(":", 2)
        if len(arg_split)==2:
            (attribute, word) = arg_split
            result[(attribute, word.lower())] = 1
        else:
            result[(None, arg.lower())] = 1
    return result

def word_search_result(archive_path, argumentList):
    words = word_dictionary(argumentList)
    archive_path = os.path.abspath(os.path.expanduser(archive_path))
    session = nucular.Nucular.Nucular(archive_path)
    query = session.Query()
    for (attribute, word_text) in words:
        for word in word_text.split():
            if attribute:
                print "searching for", repr(attribute), "containing", repr(word)
                query.attributeWord(attribute.lower(), word.lower())
            else:
                print "searching for", repr(word), "anywhere"
                query.anyWord(word.lower())
    (result, status) = query.evaluate()
    return result

def word_search(archive_path, argumentList):
    result = word_search_result(archive_path, argumentList)
    filePaths = result.identities()
    print
    for path in filePaths:
        print repr(path)
    print
    print "found", len(filePaths), "paths"

if __name__=="__main__":
    #print word_dictionary([ "Token.Name.Bogus:animals", "Token.Whatever:pig"] )
    #word_search("/tmp/repoArchive", ["Token.Name:description"])
    if len(sys.argv)<3:
        print "not enough arguments"
        print __doc__
    else:
        archive_path = sys.argv[1]
        search_parameters = sys.argv[2:]
        word_search(archive_path, search_parameters)
