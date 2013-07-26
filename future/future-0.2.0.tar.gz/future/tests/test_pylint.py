"""
This tests whether the sample little Py3 script in the README causes PyLint to squeal and protest about namespace pollution.

Ideally, the statement "from future import * should have no effect on Python 3.

"""

from __future__ import absolute_import, print_function, unicode_literals

from future import *

# New range object with slicing support
for i in range(10**11)[:10]:
    pass

# Other common iterators: map, reduce, zip
iter = zip(range(3), ['a', 'b', 'c'])
assert iter != list(iter)

# New simpler super() function:
class VerboseList(list):
    def append(self, item):
        print('Adding an item')
        super().append(item)

# These raise NameErrors:
# apply(), cmp(), coerce(), reduce(), xrange(), etc.

# This identity is restored. This is normally valid on Py3 and Py2, but
# 'from __future__ import unicode_literals' breaks it on Py2:
assert isinstance('happy', str)

