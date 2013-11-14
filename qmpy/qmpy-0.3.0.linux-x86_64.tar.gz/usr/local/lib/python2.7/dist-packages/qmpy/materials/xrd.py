from django.db import models

from qmpy.data.meta_data import *

class XRD(models.Model):
    identifier = models.CharField(max_length=100, db_index=True)
    wavelength = models.FloatField(blank=True, null=True)
    source = models.CharField(max_length=128)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'xrd'
        app_label = 'qmpy'

class Peak(models.Model):
    xrd = models.ForeignKey(XRD, related_name='peak_set')
    angle = models.FloatField()
    intensity = models.FloatField(blank=True, null=True)
    width = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'peaks'
        app_label = 'qmpy'
