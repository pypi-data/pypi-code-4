from tastypie.test import ResourceTestCase
from datetime import datetime

class WindTest(ResourceTestCase):

    def setUp(self):
        self.lat = "41.483693"
        self.lng = "-71.3264046"
        # 2013-06-29T00:00:00Z
        self.datestring = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    def test_point_prediction(self):
        """
        Tests the API for a point prediction
        
        The endpoing should return json in the following format:
        
        {
            'source': 'ucar',
            'points': [
                {
                    'time': date,
                    'lat': latitude,
                    'lon': longitude,
                    'altitude': altitude (in meters),
                    'direction': direction (in degrees),
                    'velocity': speed (in meters/second)
                },
                ...
            ]
        }
        """
        endpoint = "/winds/api/point-prediction/"
        
        url = "%s?lat=%s&lng=%s&time=%s" % (
            endpoint,
            self.lat,
            self.lng,
            self.datestring)

        resp = self.api_client.get(url, format='json')
        self.assertValidJSONResponse(resp)

        # Scope out the data for correctness.
        print resp
