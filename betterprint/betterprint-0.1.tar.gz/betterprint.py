"""

betterprint - A replacement module to pprint

Copyright Gerald Kaszuba 2007

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import pprint as orig_pprint

class MyPrettyPrinter(orig_pprint.PrettyPrinter):

    def __init__(self, indent=4, width=80, depth=None, stream=None):
        orig_pprint.PrettyPrinter.__init__(self, indent, width, depth, stream)
        self._indent = indent
        self._colours = {
            'syntax': '\x1b[0;37m',
            'key': '\x1b[0;93m',
            'value': '\x1b[0;38m',
        }

    def pprint(self, object):
        self._format(object, self._stream, self._indent, self._depth, {}, 0)
        self._stream.write('\x1b[0m')
        self._stream.write('\n')

    def pformat(self, object):
        sio = orig_pprint._StringIO()
        self._format(object, sio, self._indent, self._depth, {}, 0)
        return sio.getvalue()

    def _format(self, object, stream, indent, allowance, context, level):
        if not allowance:
            allowance = 0
        level = level + 1
        objid = id(object)
        if objid in context:
            stream.write(self._colours['value'])
            stream.write(orig_pprint._recursion(object))
            self._recursive = True
            self._readable = False
            return
        rep = self._repr(object, context, level - 1)
        typ = type(object)
        write = stream.write

        r = getattr(typ, '__repr__', None)
        if issubclass(typ, dict) and r is dict.__repr__:
            write('{')
            length = len(object)
            if length:
                write('\n')
                write((indent * level) * ' ')
                context[objid] = 1
                items  = object.items()
                items.sort()
                key, ent = items[0]
                rep = self._repr(key, context, level)
                write(self._colours['key'])
                write(rep)
                write(self._colours['syntax'])
                write(': ')
                self._format(ent, stream, indent, allowance + 1, context, \
                    level)
                for key, ent in items[1:]:
                    rep = self._repr(key, context, level)
                    write(self._colours['syntax'])
                    write(',')
                    write('\n')
                    write(' ' * (indent * level))
                    write(self._colours['key'])
                    write(rep)
                    write(self._colours['syntax'])
                    write(': ')
                    self._format(ent, stream, indent, allowance + 1, \
                        context, level)
                del context[objid]
                write(self._colours['syntax'])
                write(',')
                write('\n')
                write(' ' * (indent * (level - 1)))
            write(self._colours['syntax'])
            write('}')
            return

        if (issubclass(typ, list) and r is list.__repr__) or \
               (issubclass(typ, tuple) and r is tuple.__repr__):
            write(self._colours['syntax'])
            if issubclass(typ, list):
                write('[')
                endchar = self._colours['syntax'] + ']'
            else:
                write('(')
                endchar = self._colours['syntax'] + ')'
            length = len(object)
            if length:
                write('\n')
                write(' ' * (indent * level))
                context[objid] = 1
                self._format(object[0], stream, indent, allowance + 1, \
                    context, level)
                for ent in object[1:]:
                    write(self._colours['syntax'])
                    write(',')
                    write('\n')
                    write(' ' * (indent * level))
                    self._format(ent, stream, indent, allowance + 1, \
                        context, level)
                del context[objid]
                write(self._colours['syntax'])
                write(',')
                write('\n')
                write(' ' * (indent * (level - 1)))
            write(endchar)
            return

        write(self._colours['value'])
        write(rep)

def __pprint(object, stream=None, indent=4, width=80, depth=None):
    """Pretty-print a Python object to a stream [default is sys.stdout]."""
    printer = MyPrettyPrinter(
        stream=stream, indent=indent, width=width, depth=depth)
    printer.pprint(object)

def __pformat(object, indent=4, width=80, depth=None):
    """Format a Python object into a pretty-printed representation."""
    printer = MyPrettyPrinter(indent=indent, width=width, depth=depth)
    return printer.pformat(object)

orig_pprint.orig_pprint = __pprint
orig_pprint.orig_pformat = __pformat

pprint = __pprint
pformat = __pformat
isreadable = orig_pprint.isreadable
isrecursive = orig_pprint.isrecursive
saferepr = orig_pprint.saferepr
PrettyPrinter = orig_pprint.PrettyPrinter

if __name__ == '__main__':

    pprint([1, 2, 3, 4])
    pprint({
        1: 'a',
        2: 'b',
        3: 'c',
        4: 'd',
    })
    pprint({
        1: {},
        2: {},
        3: {},
        4: {},
    })
    pprint({
        1: {1: {}},
        2: {2: {}},
        3: {3: {}},
        4: {4: {}},
    })
    pprint({
        1: [],
        2: [],
        3: [],
        4: [],
    })
    pprint({
        'a': [],
        'b': [],
        'c': [],
        'd': [],
    })
    pprint({
        1: [[]],
        2: [[]],
        3: [[]],
        4: [[]],
    })
    pprint({
        1: (),
        2: (),
        3: (),
        4: (),
    })

    a = {}
    a[0] = a
    pprint(
        [
            [ 1, 2, 3 ],
            a,
            {
                'dict': 'moo',
                'wee': 123,
                'ert': [1,2,3],
            },
            pprint,
            'wow',
            {'lots': {'of': {'depth': {'goes': 'here'}}}}
        ],
    )

