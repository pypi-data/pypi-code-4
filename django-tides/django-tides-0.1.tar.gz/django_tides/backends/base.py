"""
    A baseclass for all tide backends
"""

UNIT_CHOICES = ('feet', 'inches', 'centimeters', 'meters')

class TideBackendBase(object):
    
    # override this value if necessary
    units = "feet"
    
    def get_station_list(self):
        """
            Returns a list of dicts with this structure:
            
                [{ 
                    'name': name,
                    'id': unique identifier,
                    'lat': latitude,
                    'lon': longitude
                },...]
        """
        raise NotImplemented

    def get_station_water_levels(self, station_id, year=None):
        """
            Returns a list of dicts with this structure:
            
                [{
                    'time': datetime object,
                    'level': float
                },...]
        """
        
        
        raise NotImplemented