import unittest

"""
Morton Numbers verfied with node-morton and a perl version of the same
"""

class TestMorton(unittest.TestCase):

    def test_get_morton(self):
        from morton import get_morton

        self.assertEqual(get_morton(1,1), 3)
        self.assertEqual(get_morton(1,2), 9)
        self.assertEqual(get_morton(2,1), 6)
        self.assertEqual(get_morton(2,2), 12)

    def test_get_latlong_morton(self):
        from morton import get_latlong_morton

        # Greenwich, England
        self.assertEqual(get_latlong_morton(0, 0), 606938688)
        # Miami, FL
        self.assertEqual(get_latlong_morton(25.7216, -80.2793), 209301296)
        # Santiago, Chile
        self.assertEqual(get_latlong_morton(-33.4500, -70.6667), 161254199)
        # Paris, France
        self.assertEqual(get_latlong_morton(48.8742, 2.3470), 624824285)
        # Cape Town, South Africa
        self.assertEqual(get_latlong_morton(-33.9767, 18.4244), 565433356)
