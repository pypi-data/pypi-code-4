
"""
Usage:

% python fsCSIbuild.py ARCHIVE_PATH DIRECTORY_ROOT

Traverse the regular files under the DIRECTORY_ROOT and attempt
to parse their lexical components.  Store successful lexical analysis
entries in a new archive at ARCHIVE_PATH.

The ARCHIVE_PATH must not exists before execution.
"""

import sys
import os
import types
import pygments.lexers
import pygments.util
import nucular.entry
import nucular.Nucular

def generate_file_descendents(path):
    "generate file paths for all regular files descending from path"
    if os.path.isfile(path):
        yield path
    elif os.path.isdir(path):
        try:
            files = os.listdir(path)
        except OSError:
            pass # maybe a permissions problem? skip it.
        else:
            for filename in files:
                child_path = os.path.join(path, filename)
                for descendent in generate_file_descendents(child_path):
                    yield descendent

def exercise_generate_file_descendents(path):
    count = 0
    for d in generate_file_descendents(path):
        print d
        count += 1
        if count>100:
            break

def get_lexer_for_file_or_None(path):
    "Find a pygments lexer appropriate for the path, or return None"
    lexer = None
    try:
        lexer = pygments.lexers.get_lexer_for_filename(path)
    except pygments.util.ClassNotFound:
        pass # no known lexer for this filename
    return lexer

def tokens_for_file(path, lexer=None, size_limit=500000):
    """
    Find lexer for path and use it to generate lexical tokens.
    Return (token_generator, lexer) or (None, None) on failure.
    """
    if lexer is None: # find a lexer, unless specified as an argument
        lexer = get_lexer_for_file_or_None(path)
    if lexer is not None:
        text = None
        try:
            text = file(path).read() # read file text
        except OSError:
            pass # read failed, maybe a permissions issue
        if text and len(text)<size_limit:
            # file is readable, not too big, and we know how to lex it: generate tokens
            return (lexer.get_tokens_unprocessed(text), lexer)
        else:
            print "WARNING: cannot read", repr(path), "or file too large"
    # return Nones if the file is too big, or unreadable, or pygments doesn't understand the format
    return (None, None)

def exercise_tokens_for_file():
    tmp_file_name = "/tmp/junk.sh"
    testfile = open(tmp_file_name, "w")
    testfile.write("""
    echo "hello world"
    echo $PATH
    exit 1
    """)
    testfile.close()
    (tokens, lexer) = tokens_for_file(tmp_file_name)
    print "parsing with lexer", lexer, "token dump follows"
    for t in tokens:
        print t
    os.unlink(tmp_file_name)

def uni(s):
    if type(s) is types.UnicodeType:
        return s
    return unicode(s, errors="ignore")

def entry_for_file(path, lexer=None, verbose=True):
    """
    Create a Nucular Entry for path mapping lexical classes to values for the file content.
    """
    (tokens, lexer) = tokens_for_file(path, lexer)
    if tokens is not None:
        if verbose:
            print '   analysing file using', lexer
        # avoid redundant inserts: precompute unique pairs of token-type to string value
        pairs = {}
        for (character_index, token_class, token_value) in tokens:
            # normalize white space in the value
            token_value = uni(token_value)
            token_value = " ".join(token_value.split())
            # if the value is not all white (empty after normalization), store it
            if token_value:
                #print token_class, type(token_class)
                token_class_name = short_name(token_class)
                pairs[ (token_class_name, token_value) ] = 1
        # unroll the pairs into an entry
        if pairs:
            entry = nucular.entry.Entry(path)
            # record the type of the file chosen by pygments
            entry["_type"] = lexer.__class__.__name__
            for (token_type_name, token_value) in pairs:
                entry[token_type_name] = token_value
            return entry
    # otherwise, no tokens were found: return None
    return None

def short_name(token_class):
    rp = repr(token_class)
    sp = rp.split(".")
    return uni(sp[-1].lower())

def exercise_entry_for_file():
    tmp_file_name = "/tmp/junk.sh"
    testfile = open(tmp_file_name, "w")
    testfile.write("""
    echo "hello world"
    python -c "print 'hello world', 2+2"
    echo $PATH
    exit 1
    """)
    testfile.close()
    print entry_for_file(tmp_file_name)
    os.unlink(tmp_file_name)

def archive_lexical_analysis_of_descendents(directory_root, archive_path, verbose=True):
    # expand paths to absolute paths
    directory_root = os.path.abspath(os.path.expanduser(directory_root))
    archive_path = os.path.abspath(os.path.expanduser(archive_path))
    if verbose:
        print "creating search archive for directory tree", repr(directory_root)
        print "at archive location", repr(archive_path)
    # make the new directory for the archive (or fail: do not overwrite!)
    os.mkdir(archive_path) # this will fail if the directory exists (for safety!)
    # find the descendents
    paths = generate_file_descendents(directory_root)
    # create the new archive
    session = nucular.Nucular.Nucular(archive_path)
    session.create()
    count = 0
    # iterate over all paths
    for path in paths:
        if verbose:
            print path
        count += 1
        entry = entry_for_file(path)
        if entry:
            session.index(entry)
        if count%100==0:
            # store the session and get a new session for each 100 files processed.
            if verbose:
                print "  ... storing at", count, path
            session.store(lazy=True)
            session = nucular.Nucular.Nucular(archive_path)
    # finalize the archive structure
    print "done parsing at", count, "now aggregating"
    session.store()
    session.aggregateRecent(fast=False, verbose=verbose)
    session.moveTransientToBase(verbose=verbose)
    if verbose:
        print "cleaning up retired files"
    session.cleanUp()
    print "archiving complete for", count, "files"

if __name__=="__main__":
    #exercise_generate_file_descendents("/")
    #exercise_tokens_for_file()
    #exercise_entry_for_file()
    #archive_lexical_analysis_of_descendents("~/junk/nucular", "/tmp/repoArchive")
    archive_path = sys.argv[1]
    directory_path = sys.argv[2]
    #import cProfile
    #cProfile.run(
    archive_lexical_analysis_of_descendents(archive_path, directory_path)
    #)

