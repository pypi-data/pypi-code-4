"""
    A baseclass for all wind backends
"""

UNIT_CHOICES = ('m/s', 'knots')

class WindBackendBase(object):
    
    # override this value if necessary
    units = "m/s"
    
    def get_wind_at_point(self, lat, lng, start_time):
        """
            Returns a list of dicts with this structure:
            
                [{ 
                    'time': datetime,
                    'lat': latitude,
                    'lon': longitude,
                    'altitude': altitude (in meters),
                    'direction': direction (in degrees),
                    'velocity': speed (in meters/second)
                },...]
                
            The lat and lng are the latitude and longitude coordinates for the point in question.
        """
        raise NotImplemented