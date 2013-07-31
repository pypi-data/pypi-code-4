# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
from __future__ import unicode_literals

from django.db import models

class HwModel(models.Model):
    model = models.CharField(max_length=255L, primary_key=True, unique=True)
    cpu = models.CharField(max_length=255L)
    ram = models.CharField(max_length=255L)
    def __unicode__(self):
        return self.model
    class Meta:
        db_table = 'hw_model'

class NetInfo(models.Model):
    gateway = models.CharField(max_length=255L)
    mask = models.CharField(max_length=20L,default="255.255.255.0")
    vlan = models.IntegerField(primary_key=True)
    net_addr = models.CharField(max_length=255L)
    def __unicode__(self):
        return str(self.vlan)
    class Meta:
        db_table = 'net_info'
        
class Switch(models.Model):
    sw_name = models.CharField(max_length=255L)
    vlan = models.ForeignKey(NetInfo, db_column="vlan")
    id = models.IntegerField(primary_key=True)
    def __unicode__(self):
        return self.sw_name+" | "+str(self.vlan.vlan)
    class Meta:
        db_table = 'switch'

class Os(models.Model):
    id = models.IntegerField(primary_key=True)
    family = models.CharField(max_length=255L)
    version = models.CharField(max_length=255L)
    def __unicode__(self):
        return self.family+self.version
    class Meta:
        db_table = 'os'

class Profile(models.Model):
    name = models.CharField(max_length=255L,primary_key=True)
    url = models.CharField(max_length=255L)
    def __unicode__(self):
        return self.name
    class Meta:
        db_table = 'profile'
        
class Step(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=255L)
    def __unicode__(self):
        return str(self.id)
    class Meta:
        db_table = 'step'
        
class JobTracker(models.Model):
    svctag = models.CharField(max_length=255L, primary_key=True)
    status = models.ForeignKey(Step,db_column='status')
    mod_time = models.DateTimeField()
    started = models.DateTimeField()
    hostname = models.CharField(max_length=255L, unique=True)
    os_id = models.ForeignKey(Os, db_column="os_id")
    net_info_id = models.ForeignKey(NetInfo, db_column="net_info_id")
    profile = models.ForeignKey(Profile, db_column="profile")
    def __unicode__(self):
        return self.svctag
    class Meta:
        db_table = 'job_tracker'

class SwitchPort(models.Model):
    mac = models.CharField(max_length=255L, primary_key=True)
    name = models.CharField(max_length=255L)
    module = models.IntegerField()
    port = models.IntegerField()
    def __unicode__(self):
        return self.mac
    class Meta:
        db_table = 'switch_port'

class Machine(models.Model):
    svctag = models.CharField(max_length=255L, primary_key=True)
    hw_model_id = models.ForeignKey(HwModel, db_column="hw_model_id")
    mac = models.CharField(max_length=255L)
    def __unicode__(self):
        return self.svctag
    class Meta:
        db_table = 'machine'
