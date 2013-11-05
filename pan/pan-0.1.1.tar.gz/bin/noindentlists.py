#!/usr/bin/python

"""
Don't indent the paragraph after lists
"""

from pan.pandoc import toJSONFilter

def noindentlists(key, value, format, **meta):
    if key in ['BulletList', 'OrderedList', 'CodeBlock', 'BlockQuote']:
        return [{key: value},{"Para":[{"RawInline":["tex", r"\noindent"]}]}]

if __name__ == "__main__":
    toJSONFilter(noindentlists)
