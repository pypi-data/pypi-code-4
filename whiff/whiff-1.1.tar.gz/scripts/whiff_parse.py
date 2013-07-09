#!/usr/bin/env python

"""
Script to parse a whiff configuration file.
This is only useful for syntax checking.
"""

from whiff import parseTemplate

def testparse(filepath):
    text = open(filepath).read()
    (test, result, cursor) = parseTemplate.parse_page(text, file_path=filepath)
    if not test:
        raise ValueError, "whiff template parse failed: "+repr((result, cursor))
    if cursor<len(text):
        raise ValueError, "test case page not consumed "+repr(text[cursor:cursor+100])
    print "parse succeeded"

if __name__=="__main__":
    import sys
    testparse(*sys.argv[1:])
