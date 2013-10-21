# -*- coding: utf-8 -*-

# Copyright 2013 Vincent Jacques
# vincent@vincent-jacques.net

# This file is part of MockMockMock. http://jacquev6.github.com/MockMockMock

# MockMockMock is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# MockMockMock is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with MockMockMock.  If not, see <http://www.gnu.org/licenses/>.

import unittest
import os.path
import sys
atLeastPython3 = sys.hexversion >= 0x03000000

import MockMockMock


class TestException(Exception):
    pass


class SystemCalls(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.mocks = MockMockMock.Engine()

    def testMockGloballyImportedFunction(self):
        original = os.path.exists
        m = self.mocks.replace("os.path.exists")
        m.expect("foo").andReturn(True)
        self.assertTrue(os.path.exists("foo"))
        self.mocks.tearDown()
        self.assertIs(os.path.exists, original)
        self.assertFalse(os.path.exists("foo"))

    def testMockLocallyImportedFunction(self):
        import subprocess
        original = subprocess.check_output
        m = self.mocks.replace("subprocess.check_output")
        m.expect(["foo", "bar"]).andReturn("baz\n")
        self.assertEqual(subprocess.check_output(["foo", "bar"]), "baz\n")
        self.mocks.tearDown()
        self.assertIs(subprocess.check_output, original)
        self.assertEqual(subprocess.check_output(["echo", "toto"]), b"toto\n" if atLeastPython3 else "toto\n")
