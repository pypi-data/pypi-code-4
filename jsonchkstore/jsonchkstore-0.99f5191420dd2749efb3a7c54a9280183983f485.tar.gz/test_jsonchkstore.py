#! /usr/bin/env python

import os
import unittest

from test_chkstore import TmpDirMixin

from jsonchkstore import JsonCHKStore


class JsonCHKStoreTests (TmpDirMixin, unittest.TestCase):
    def setUp(self):
        TmpDirMixin.setUp(self)

        path = os.path.join(self.tmpdir, 'store')

        JsonCHKStore.initialize_storage_directory(path)
        self._store = JsonCHKStore(path)

    def test_insert_and_read(self):
        input = {
            'a string': 'is untied',
            'a bool': True,
            'nothing': None,
            'a float': 2.3,
            'an int': 7,
            'an array': [2, 'apple'],
            'an object': {'x': 42},
            }

        key = self._store.insert_json(input)
        output = self._store.read_json(key)

        self.assertEqual(input, output)


if __name__ == '__main__':
    unittest.main()
