#! /usr/bin/env python

import sys
import argparse
import simplejson

from chkstore import CHKStore


class JsonCHKStore (CHKStore):
    def read_json(self, key):
        with self.open_reader(key) as f:
            return simplejson.load(f)

    def insert_json(self, fields):
        return write_canonical_json(self.open_inserter(), fields).close()


def write_canonical_json(f, fields):
    simplejson.dump(
        obj = fields,
        fp = f,

        # These json options are required for canonicalization:
        encoding = 'utf8',
        indent = 2,
        sort_keys = True,
        check_circular = True,
        )
    return f


if __name__ == '__main__':
    main()
