# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'AcquisitionSessionConfig.started'
        db.add_column(u'acquisition_acquisitionsessionconfig', 'started',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'AcquisitionSessionConfig.completed'
        db.add_column(u'acquisition_acquisitionsessionconfig', 'completed',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'DataCollectorConfig.started'
        db.add_column(u'acquisition_datacollectorconfig', 'started',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'DataCollectorConfig.completed'
        db.add_column(u'acquisition_datacollectorconfig', 'completed',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'DataCollectorConfig.running_instance_id'
        db.add_column(u'acquisition_datacollectorconfig', 'running_instance_id',
                      self.gf('django.db.models.fields.CharField')(max_length=128, unique=True, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'AcquisitionSessionConfig.started'
        db.delete_column(u'acquisition_acquisitionsessionconfig', 'started')

        # Deleting field 'AcquisitionSessionConfig.completed'
        db.delete_column(u'acquisition_acquisitionsessionconfig', 'completed')

        # Deleting field 'DataCollectorConfig.started'
        db.delete_column(u'acquisition_datacollectorconfig', 'started')

        # Deleting field 'DataCollectorConfig.completed'
        db.delete_column(u'acquisition_datacollectorconfig', 'completed')

        # Deleting field 'DataCollectorConfig.running_instance_id'
        db.delete_column(u'acquisition_datacollectorconfig', 'running_instance_id')


    models = {
        u'acquisition.acquisitionsessionconfig': {
            'Meta': {'ordering': "['created']", 'object_name': 'AcquisitionSessionConfig'},
            'completed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'started': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'temporary': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'acquisition.datacollectorconfig': {
            'Meta': {'object_name': 'DataCollectorConfig'},
            'completed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_acquisition.datacollectorconfig_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'running_instance_id': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'session_config': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'collectors'", 'to': u"orm['acquisition.AcquisitionSessionConfig']"}),
            'started': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['acquisition']