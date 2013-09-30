class SearchLocation(dict):

    def __init__(self, latitude, longitude, accuracy=None, altitude=None, altitude_accuracy=None):
        super(SearchLocation, self).__init__()
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.accuracy = float(accuracy) if accuracy != None else None
        self.altitude = float(altitude) if altitude != None else None
        self.altitude_accuracy = float(altitude_accuracy) if altitude_accuracy != None else None

    def validate(self):
        assert self.latitude != None
        assert self.longitude != None

    def __str__(self):
       return unicode(self).encode("utf-8")

    def __unicode__(self):
        self.validate()
        loc = "{0:f},{1:f}".format(self.latitude, self.longitude)
        if self.accuracy != None:
            loc = "{0},{1:f}".format(loc, self.accuracy)
        if self.altitude != None:
            loc = "{0},{1:f}".format(loc, self.altitude)
        if self.altitude_accuracy != None:
            loc = "{0},{1:f}".format(loc, self.altitude_accuracy)
        return loc 
