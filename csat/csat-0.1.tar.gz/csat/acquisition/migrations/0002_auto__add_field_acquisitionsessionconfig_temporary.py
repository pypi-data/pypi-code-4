# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'AcquisitionSessionConfig.temporary'
        db.add_column(u'acquisition_acquisitionsessionconfig', 'temporary',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'AcquisitionSessionConfig.temporary'
        db.delete_column(u'acquisition_acquisitionsessionconfig', 'temporary')


    models = {
        u'acquisition.acquisitionsessionconfig': {
            'Meta': {'object_name': 'AcquisitionSessionConfig'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'temporary': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'acquisition.datacollectorconfig': {
            'Meta': {'object_name': 'DataCollectorConfig'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_acquisition.datacollectorconfig_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'session_config': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'collectors'", 'to': u"orm['acquisition.AcquisitionSessionConfig']"})
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