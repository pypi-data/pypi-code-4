"""
    The backend for the US' NOAA
"""
from base import TideBackendBase

import requests
import datetime
from bs4 import BeautifulSoup

class NOAABackend(TideBackendBase):
    
    name = 'noaa'
    
    def get_station_list(self):
        """
            Pulls the JSON from the NOAA tides & currents interface
            
            [{ 
                'name': name,
                'id': unique identifier,
                'lat': latitude,
                'lon': longitude
            },...]
            
        """
        json_url =  ("http://tidesandcurrents.noaa.gov/cgi-bin/map2/odinmap.cgi?"
                    "type=TidePredictions&nelat=90&nelng=180&swlat=-90&"
                    "swlng=-180&mode=json")
        r = requests.get(json_url)
        stations = r.json()
        
        station_list = []
        
        for l in stations["locations"]:
            station_list.append({
                                    "name": l['name'],
                                    "id": l["stnid"],
                                    "lat": l['lat'],
                                    "lon": l["lng"]
            })
        return station_list
        
        
    def get_station_water_levels(self, station_id, year=None):
        """
            Extracts the XML from the tides & currents website
            
            [{
                'time': datetime object,
                'level': float
            },...]
        """
        
        if not year:
            year = datetime.date.today().year
        
        water_level_list = []
        xml_url = (
                    "http://tidesandcurrents.noaa.gov/noaatidepredictions/NOAATidesFacade.jsp?"
                    "datatype=Annual+XML&Stationid=%s&"
                    "bdate=%d0101&"
                    "edate=%d0131&"
                    "timeUnits=1&"
                    "timeZone=2"
        )
        
        r = requests.get(xml_url % (station_id, year, year))
        soup = BeautifulSoup(r.content)
        items = soup.findAll('item')
        
        table = []
        
        for i in items:
            d = "%s %s" % (i.find("date").text, i.find('time').text)
            table.append({
                "time": datetime.datetime.strptime(d, "%Y/%m/%d %H:%M"),
                "level": float(i.find('predictions_in_ft').text)
            })
        
        return table
