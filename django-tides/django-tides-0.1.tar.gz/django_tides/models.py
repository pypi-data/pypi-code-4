from django.db import models
from django.contrib.gis.db import models as geomodels

SOURCE_CHOICES = (('noaa', "NOAA"))

class TideStation(models.Model):
    name = models.CharField(max_length=255)
    point = geomodels.PointField(geography=True, dim=3)
    source = models.CharField(default='noaa', max_length=8)
    source_id = models.CharField(max_length=8)
    objects = geomodels.GeoManager()
    
    def __unicode__(self):
        return self.name
    
class WaterLevel(models.Model):
    station = models.ForeignKey('TideStation')
    level = models.FloatField()
    time = models.DateTimeField()
    
    def __unicode__(self):
        return "%s %s" % (self.station.name, self.time)