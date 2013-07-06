# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AcquisitionSessionConfig'
        db.create_table(u'acquisition_acquisitionsessionconfig', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('description', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'acquisition', ['AcquisitionSessionConfig'])

        # Adding model 'DataCollectorConfig'
        db.create_table(u'acquisition_datacollectorconfig', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('polymorphic_ctype', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'polymorphic_acquisition.datacollectorconfig_set', null=True, to=orm['contenttypes.ContentType'])),
            ('session_config', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['acquisition.AcquisitionSessionConfig'])),
        ))
        db.send_create_signal(u'acquisition', ['DataCollectorConfig'])


    def backwards(self, orm):
        # Deleting model 'AcquisitionSessionConfig'
        db.delete_table(u'acquisition_acquisitionsessionconfig')

        # Deleting model 'DataCollectorConfig'
        db.delete_table(u'acquisition_datacollectorconfig')


    models = {
        u'acquisition.acquisitionsessionconfig': {
            'Meta': {'object_name': 'AcquisitionSessionConfig'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'acquisition.datacollectorconfig': {
            'Meta': {'object_name': 'DataCollectorConfig'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_acquisition.datacollectorconfig_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'session_config': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['acquisition.AcquisitionSessionConfig']"})
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