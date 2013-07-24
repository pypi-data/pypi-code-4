from base import WindBackendBase

import requests
import datetime
from bs4 import BeautifulSoup

class UCARBackend(WindBackendBase):
    """
        The UCAR backend for wind prediction data
    """
    
    def get_wind_at_point(self, lat, lng, time):
        """
            This will attempt to get all wind prediction within 30 days of time
            
            @todo: this is a bit of a hack. Eventually, it would be nice to 
            detect the timezone of the lat/lng and pick the exact window
            allowed by UCAR... and maybe not even hit UCAR if it's outside of
            that window.
        """
    
        start_time = time - datetime.timedelta(days=30)
        end_time = time + datetime.timedelta(days=30)
    
        xml_url = (
                "http://thredds.ucar.edu/thredds/ncss/grid/grib/NCEP/NDFD/CONUS_5km/best"
                "?var=Wind_direction_from_which_blowing_height_above_ground"
                "&var=Wind_speed_height_above_ground"
                "&latitude=%s"
                "&longitude=%s"
                "&time_start=%s"
                "&time_end=%s"
                "&vertCoord="
                "&accept=xml"
        )
    
        r = requests.get(xml_url % (lat, lng, start_time, end_time))
        soup = BeautifulSoup(r.content)
        points = soup.findAll('point')
        
        point_list = []
        
        for p in points:
            point_list.append({
                "time": datetime.datetime.strptime(p.find("data", {"name":"date"}).text, "%Y-%m-%dT%H:%M:%SZ"),
                "lat": float(p.find("data", {"name":"lat"}).text),
                "lon": float(p.find("data", {"name":"lon"}).text),
                "altitude": float(p.find("data", {"name":"vertCoord"}).text),
                "direction": float(p.find("data", {"name":"Wind_direction_from_which_blowing_height_above_ground"}).text),
                "velocity": float(p.find("data", {"name":"Wind_speed_height_above_ground"}).text)
            })
        
        return point_list