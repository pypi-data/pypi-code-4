from __future__ import unicode_literals

from django.test import TestCase

from nodetree.maps import SimpleMap


class TestSimpleMap(TestCase):

    def setUp(self):
        self.map = SimpleMap()

    def test_instantiation(self):
        self.assertIsInstance(self.map._map, dict)

    def test_set_method(self):
        self.map.set('One', 1)

        self.assertEqual(len(self.map._map), 1)
        self.assertTrue(self.map.has('One'))
        self.assertFalse(self.map.has('Two'))
        self.assertRaises(KeyError, self.map.set, 'One', 1)

        self.map.set('Two', 2)

        self.assertEqual(len(self.map._map), 2)
        self.assertTrue(self.map.has('One'))
        self.assertTrue(self.map.has('Two'))
        self.assertRaises(KeyError, self.map.set, 'Two', 1)

    def test_remove_method(self):
        self.map.set('One', 1)
        self.map.set('Two', 2)

        self.map.remove('One')

        self.assertEqual(len(self.map._map), 1)
        self.assertEqual(self.map.length(), 1)
        self.assertFalse(self.map.has('One'))
        self.assertTrue(self.map.has('Two'))
        self.assertRaises(KeyError, self.map.remove, 'One')

        self.map.remove('Two')

        self.assertEqual(len(self.map._map), 0)
        self.assertEqual(self.map.length(), 0)
        self.assertFalse(self.map.has('One'))
        self.assertFalse(self.map.has('Two'))
        self.assertRaises(KeyError, self.map.remove, 'Two')

    def test_has_method(self):
        self.map.set('One', 1)

        self.assertTrue(self.map.has('One'))
        self.assertFalse(self.map.has('Two'))

    def test_get_method(self):
        self.map.set('One', 1)
        self.map.set('Two', 2)

        self.assertEqual(self.map.get('One'), 1)
        self.assertEqual(self.map.get('Two'), 2)
        self.assertIsNone(self.map.get('Three'))

    def test_values_method(self):
        self.map.set('One', 1)
        self.map.set('Two', 2)

        self.assertTrue(1 in self.map.values() and 2 in self.map.values())
        self.assertTrue(1 in self.map.values('One') and not 2 in self.map.values('One'))
        self.assertTrue(not 1 in self.map.values('Two') and 2 in self.map.values('Two'))
        self.assertTrue(1 in self.map.values('One', 'Two') and 2 in self.map.values('One', 'Two'))


    def test_keys_method(self):
        self.map.set('One', 1)
        self.map.set('Two', 2)

        self.assertIn('One', self.map.keys())
        self.assertIn('Two', self.map.keys())

        self.map.remove('One')
        self.assertIn('Two', self.map.keys())
        self.assertFalse('One' in self.map.keys())


