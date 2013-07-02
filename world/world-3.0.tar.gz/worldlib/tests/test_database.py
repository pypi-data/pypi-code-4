# Copyright (C) 2013 by Barry A. Warsaw
#
# This file is part of world
#
# world is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, version 3 of the License.
#
# world is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# world.  If not, see <http://www.gnu.org/licenses/>.

"""Test the Database class."""

__all__ = [
    'TestDatabase',
    ]


import os
import pickle
import shutil
import hashlib
import tempfile
import unittest

from pkg_resources import resource_filename
from worldlib.database import Database


class TestDatabase(unittest.TestCase):
    def test_no_cache(self):
        db = Database()
        self.assertEqual(db.lookup_code('it'), 'ITALY')

    def test_cache(self):
        # The constructor takes a cache argument.
        tempdir = tempfile.mkdtemp()
        try:
            # Make a copy of the cached pickle, with some modifications so
            # it's easy to tell which one we've got.
            old_cache = resource_filename('worldlib.data', 'codes.pck')
            with open(old_cache, 'rb') as fp:
                mappings = pickle.load(fp)
            new_mappings = {}
            for key, value in mappings.items():
                if not isinstance(value, bytes):
                    value = value.encode('utf-8')
                new_mappings[key] = hashlib.sha1(value).hexdigest()
            path = os.path.join(tempdir, 'codes.pck')
            with open(path, 'wb') as fp:
                pickle.dump(new_mappings, fp)
            db = Database(path)
        finally:
            shutil.rmtree(tempdir)
        # SHA1 hash of ITALY
        self.assertEqual(db.lookup_code('it'),
                         '50c8232b82ba3764a4a2a8f4801de058bd3c3cc9')

    def test_find_matches(self):
        db = Database()
        matches = db.find_matches('italy')
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0], ('it', 'ITALY'))

    def test_find_matches_uppercase(self):
        db = Database()
        matches = db.find_matches('ITALY')
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0], ('it', 'ITALY'))

    def test_find_matches_multiple(self):
        db = Database()
        matches = db.find_matches('united')
        self.assertEqual(len(matches), 6)
        self.assertEqual(sorted(matches), [
            ('ae', 'UNITED ARAB EMIRATES'),
            ('gb', 'UNITED KINGDOM'),
            ('tz', 'TANZANIA, UNITED REPUBLIC OF'),
            ('uk', 'United Kingdom (common practice)'),
            ('um', 'UNITED STATES MINOR OUTLYING ISLANDS'),
            ('us', 'UNITED STATES'),
            ])

    def test_iteration(self):
        codes = []
        for code in Database():
            codes.append(code)
        top_5 = sorted(codes)[:5]
        self.assertEqual(top_5, ['ac', 'ad', 'ae', 'aero', 'af'])
