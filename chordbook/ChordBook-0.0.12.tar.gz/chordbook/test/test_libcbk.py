"""Unit tests for libcbk.py"""

import chordbook.libcbk as libcbk

import unittest

class TestTune(unittest.TestCase):
    """Tests for libcbk.Tune object"""

    def test__init__(self):
        """Ensure Tune() returns a Tune object"""

        tune = libcbk.Tune()
        self.assert_(isinstance(tune, libcbk.Tune))

    def test__repr__(self):
        """Ensure __repr__ behaves as expected"""

        expected = "<class 'chordbook.libcbk.Tune'>({'transpose': '', 'key': ''})"

        tune = libcbk.Tune()
        self.assertEqual(tune.__repr__(), expected)


class TestBook(unittest.TestCase):
    """Tests for libcbk.Book object"""

    def test__init__(self):
        """Ensure Book() returns a Book object"""

        book = libcbk.Book()
        self.assert_(isinstance(book, libcbk.Book))

    def test__repr__(self):
        """Ensure __repr__ behaves as expected"""

        expected = "<class 'chordbook.libcbk.Book'>({'tunes': [], 'band': '', 'version': '', 'filename': ''})"

        book = libcbk.Book()
        self.assertEqual(book.__repr__(), expected)

if __name__ == '__main__':
    unittest.main()
