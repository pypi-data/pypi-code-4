class SearchBounds(object):

    def __init__(self, sw_latitude, sw_longitude, ne_latitude, ne_longitude):
        self.sw_latitude = float(sw_latitude)
        self.sw_longitude = float(sw_longitude)
        self.ne_latitude = float(ne_latitude)
        self.ne_longitude = float(ne_longitude)

    def __str__(self):
       return unicode(self).encode("utf-8")

    def __unicode__(self):
        return "{:f},{:f}|{:f},{:f}".format(self.sw_latitude, self.sw_longitude, self.ne_latitude, self.ne_longitude)
        
