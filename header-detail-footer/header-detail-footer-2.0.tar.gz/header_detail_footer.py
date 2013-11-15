########################################################################
# Handle parsing text files with a fixed number of header rows, and a
#  fixed number of footer rows.
#
# Copyright 2013 True Blade Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Notes:
#  The input does not have to be a file, it's just an iterable of any
#   sort.
#  Does not strip newlines (or anything else) from the input. If you
#   want that, do it in the input iterator.
########################################################################

from __future__ import print_function
from collections import deque

__all__ = ['HeaderError', 'FooterError', 'parse']

class _iterator_with_count(object):
    def __init__(self, it):
        self._it = it
        self.count = 0

    def __next__(self):
        n = next(self._it)  # do this first, so if StopIteration is raised
                            #  the rest is not executed
        self.count += 1
        return n
    next = __next__         # for python 2

    def __iter__(self):
        return self


class HeaderError(ValueError): pass
class FooterError(ValueError): pass

# returns raw rows from the input
#  assumes an n row header and an m row footer. n and m default to 1, can be zero
class _HeaderDetailFooterRows(object):
    def __init__(self, input, header_rows=1, footer_rows=1):
        self.input = input
        self.headers = []
        self.footers = deque()

        self.details_exhausted = False

        # read the headers, then read the footer cache
        # this all happens in __init__ so all header/footer related
        #  errors occur here, as opposed to in various other methods
        # it also means that header() and footer() never need to
        #  be called at all
        # footer() can only be called after details() is exhausted
        try:
            self._read_rows(header_rows, self.headers)
        except StopIteration:
            raise HeaderError('too few rows for header')

        try:
            self._read_rows(footer_rows, self.footers)
        except StopIteration:
            raise FooterError('too few rows for footer')

    def _read_rows(self, n, into):
        for i in range(n):
            into.append(next(self.input))

    def header(self):
        if len(self.headers) == 1:
            return self.headers[0]
        else:
            return self.headers

    def details(self):
        return _iterator_with_count(self._details())

    def _details(self):
        for row in self.input:
            # push this onto the queue, then return what we pop. this keeps
            #  the footers intact, and works if there are zero footer rows
            self.footers.append(row)
            yield self.footers.popleft()
        self.details_exhausted = True

    def footer(self):
        if not self.details_exhausted:
            raise ValueError('called footer() before details were exhausted')
        if len(self.footers) == 1:
            return self.footers[0]
        else:
            # convert to a list, just to be consistent with headers()
            return list(self.footers)


def parse(input, header_rows=1, footer_rows=1):
    '''Returns a 3-tuple (header, details, footer). header is the headers,
    details is an iterator over the details, and footer is a callable returning
    the footers. footer can only be called when details is exhausted.

    If header_rows is one, header contains the header, else it is a list of
    headers.'''
    parser = _HeaderDetailFooterRows(iter(input), header_rows, footer_rows)
    return parser.header(), parser.details(), parser.footer


if __name__ == '__main__':
    import unittest

    class TestCaseReadrows(unittest.TestCase):
        def test_simple(self):
            header, details, footer = parse('abc')
            self.assertEqual(details.count, 0)
            self.assertEqual(header, 'a')
            self.assertEqual(list(details), ['b'])
            self.assertEqual(footer(), 'c')
            self.assertEqual(details.count, 1)

        def test_multirow(self):
            header, details, footer = parse('abcdef')
            self.assertEqual(header, 'a')
            self.assertEqual(list(details), ['b', 'c', 'd', 'e'])
            self.assertEqual(details.count, 4)
            self.assertEqual(footer(), 'f')

        def test_no_detail_rows(self):
            header, details, footer = parse('ab')
            self.assertEqual(header, 'a')
            self.assertEqual(list(details), [])
            self.assertEqual(footer(), 'b')
            self.assertEqual(details.count, 0)

        def test_missing_rows(self):
            with self.assertRaises(HeaderError):
                header, details, footer = parse('')

        def test_missing_footer(self):
            with self.assertRaises(FooterError):
                header, details, footer = parse('a')

        def test_no_header(self):
            header, details, footer = parse('abc', header_rows=0)
            self.assertEqual(len(header), 0)
            self.assertEqual(list(details), ['a', 'b'])
            self.assertEqual(footer(), 'c')

        def test_no_footer(self):
            header, details, footer = parse('abc', footer_rows=0)
            self.assertEqual(header, 'a')
            self.assertEqual(list(details), ['b', 'c'])
            self.assertEqual(footer(), [])

        def test_multi_row_header_no_footer(self):
            header, details, footer = parse('abcdef', header_rows=3, footer_rows=0)
            self.assertEqual(header, ['a', 'b', 'c'])
            self.assertEqual(list(details), ['d', 'e', 'f'])
            self.assertEqual(footer(), [])

        def test_no_header_multi_row_footer(self):
            header, details, footer = parse('abcdef', header_rows=0, footer_rows=3)
            self.assertEqual(header, [])
            self.assertEqual(list(details), ['a', 'b', 'c'])
            self.assertEqual(footer(), ['d', 'e', 'f'])

        def test_no_header_no_footer_no_details(self):
            header, details, footer = parse('', header_rows=0, footer_rows=0)
            self.assertEqual(header, [])
            self.assertEqual(list(details), [])
            self.assertEqual(footer(), [])

        def test_no_header_no_footer(self):
            header, details, footer = parse('a', header_rows=0, footer_rows=0)
            self.assertEqual(header, [])
            self.assertEqual(list(details), ['a'])
            self.assertEqual(footer(), [])

        def test_details_only_no_header_footer(self):
            _, details, _ = parse('abc', header_rows=0, footer_rows=0)
            self.assertEqual(list(details), ['a', 'b', 'c'])

        def test_details_only_with_header_footer(self):
            _, details, _ = parse('abcde', header_rows=2, footer_rows=3)
            self.assertEqual(list(details), [])

            _, details, _ = parse('abABCcde', header_rows=2, footer_rows=3)
            self.assertEqual(list(details), ['A', 'B', 'C'])

        def test_only_calling_footer(self):
            header, details, footer = parse('abc', footer_rows=2)
            self.assertRaises(ValueError, footer)

        def test_not_exhausting_details(self):
            header, details, footer = parse('abcdef')
            self.assertEqual(next(details), 'b')
            self.assertEqual(next(details), 'c')
            self.assertRaises(ValueError, footer)
            # now read the rest of the details
            self.assertEqual(list(details), ['d', 'e'])
            # now footer will succeed
            self.assertEqual(footer(), 'f')


    unittest.main()
