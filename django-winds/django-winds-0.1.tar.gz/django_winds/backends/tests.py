from django_winds.backends import BACKENDS
import unittest
import datetime

class TestBackends(unittest.TestCase):
    
    def setUp(self):
        self.lat = "41.483693"
        self.lng = "-71.3264046"
        self.time = datetime.datetime.now()

    def test_backends(self):
        for k,klass in BACKENDS.items():
            backend = klass()
            point_list = backend.get_wind_at_point(self.lat, self.lng, self.time)
            
            # just confirm the correct value-types are being returned
            self.assertIsInstance(point_list[0]['time'], datetime.datetime)
            self.assertIsInstance(point_list[0]['velocity'], float)

if __name__ == '__main__':
    unittest.main()