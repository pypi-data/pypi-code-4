#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from subprocess import Popen, PIPE
import _ikedarts

def mkdarts(words, darts_file='./test.darts', mkdarts_cmd='/usr/bin/mkdarts'):
    """Compile unicode words into darts file.
       Alternatively, darts file can be built with the underlying mkdarts command, like:
       cat /usr/share/dict/words | env LC_ALL=C sort -u | mkdarts /dev/stdin words.darts
    """

    if not os.path.exists(mkdarts_cmd):
        raise RuntimeError('mkdarts command not found. please install darts.', mkdarts_cmd)

    if os.path.exists(darts_file):
        os.unlink(darts_file)

    entries=sorted([ w.encode('utf8') for w in words if w ])

    p=Popen([mkdarts_cmd, '/dev/stdin', darts_file], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    for w in entries:
        p.stdin.write(w+'\n')
    p.stdin.close()
    return (darts_file, p.wait(), p.stdout.read(), p.stderr.read())

class IkeDarts(object):
    """search in terface to DARTS"""
    
    def __init__(self, dictionary_path):
        """instantiate the search object and attach the dictionary file"""

        if not os.path.exists(dictionary_path):
            raise RuntimeError('no such darts file', dictionary_path)

        self.ikd=_ikedarts.ikedarts_init()
        assert _ikedarts.ikedarts_open(self.ikd, dictionary_path) is None, \
            "failed to open %s" % dictionary_path

    def search(self, text):
        """return matching entries.
        list of dict with entry, key, offset are returned.
             {'entry': 'foo', 'key': 2, 'offset': 7}
        * entry:  the matching word.
        * key:    zero-based offset of the word as is was fed to mkdarts.
        * offset: byte-offset of the match in the text.
        
        Matching semantics:
        for dictionary of entries: bar,baz,foo,foobar
        and document: 'oh hai foo foobar hobaz somebar hoge', 
        following match list is returend:
        [
                # whole words are obviously found.
                {'entry': 'foo', 'key': 2, 'offset': 7},

                # entry that is a prefix is also found
                {'entry': 'foo', 'key': 2, 'offset': 11},

                # longer entries are also found.
                # ie all entries that are prefixes at a point in the documents are found.
                # Note, however, that 'bar' embedded in 'foobar' is missed.
                # So an entry is shadowed by a preceeding match. This is a known limitation.
                {'entry': 'foobar', 'key': 3, 'offset': 11},

                # match in the middle of a word.
                {'entry': 'baz', 'key': 1, 'offset': 20},

                # If the preceeding prefix is not matched, an embedded bar is found.
                # To summarise:
                #   bar in foobar is missed since foo matched.
                #   bar in somebar is matched since some is not an entry.
                {'entry': 'bar', 'key': 0, 'offset': 28},
           ]
        """

        result=[]
        def visit(t, off, blen, key):
            result.append(dict(offset=off, entry=t[:blen], key=key))
        _ikedarts.ikedarts_search(self.ikd, text, visit);
        return result

def main():

    import sys

    _,dictionary_file=sys.argv

    ikd=IkeDarts(dictionary_file)
    for line in sys.stdin.readlines():
        line=line.strip()
        print '+'+line
        for r in ikd.search(line):
            print '-'+' ' * r['offset'] + r['entry']

if __name__=='__main__':

    main()
