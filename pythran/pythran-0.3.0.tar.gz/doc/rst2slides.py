import re
import sys

MAXLINE = 60

input = sys.argv[1] if len(sys.argv) > 1 else sys.stdin
header = sys.argv[2] if len(sys.argv) > 2 else ''
footer = sys.argv[3] if len(sys.argv) > 3 else ''
extra = sys.argv[4] if len(sys.argv) > 4 else ''

with file(input) as fd:
    content = fd.read()
    sections = re.findall(r'\n(.*?)\n-----*\n', content)
    sections_content = content.split('---\n')
    sections_content = sections_content[1:]  # skip intro

    if extra:
        print file(extra).read()

    for i, c in enumerate(sections_content):
        code_title = sections[i]
        codes = re.findall(r'::\n\n(.*?)\n\n', c, re.DOTALL)

        for j, the_code in enumerate(codes):
            the_title = code_title + ' ({})'.format(j)
            the_formatted_code = []
            for line in the_code.split('\n'):
                for i in xrange(0, len(line), MAXLINE):
                    pad = '  ' if i else ''
                    the_formatted_code.append(pad + line[i:i+MAXLINE])

            print the_title
            print '-'*len(the_title)
            print
            print '.. code-block:: python'
            print
            print '\n'.join(the_formatted_code)
            print

    if header:
        print '.. header::'
        print
        print '    ' + header
        print

    if footer:
        print '.. footer::'
        print
        print '    ' + footer
        print




