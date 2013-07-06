# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'DataCollectorConfig', fields ['running_instance_id']
        db.delete_unique(u'acquisition_datacollectorconfig', ['running_instance_id'])


    def backwards(self, orm):
        # Adding unique constraint on 'DataCollectorConfig', fields ['running_instance_id']
        db.create_unique(u'acquisition_datacollectorconfig', ['running_instance_id'])


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
            'running_instance_id': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
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