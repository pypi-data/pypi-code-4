from __future__ import print_function

import re
import logging
import sys

from Yaco import Yaco
import leip

from mad2.util import  get_filenames, get_all_mad_files

lg = logging.getLogger(__name__)

def _getter(o, k):
    assert(isinstance(o, Yaco))
    if '.' in k:
        k1, k2 = k.split('.', 1)
        return _getter(o[k1], k2)
    else:
        return o[k]


@leip.arg('-s', '--sep',  help='separator', default='\t')
@leip.arg('key', help='keys to display', nargs='+')
@leip.command
def table(app, args):
    """
    Create a table
    """
    print('#' + args.sep.join(map(str, args.key)))
    for madfile in get_all_mad_files(app, args):
        values = []
        for k in args.key:
            vv = _getter(madfile.mad, k)
            if str(vv) == '{}':
                vv = _getter(madfile.otf, k)
            if str(vv) == '{}':
                vv = ""
            values.append(vv)

        print(args.sep.join(map(str, values)))







