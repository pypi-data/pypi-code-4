# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'RandomConfig'
        db.create_table(u'random_randomconfig', (
            (u'datacollectorconfig_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['acquisition.DataCollectorConfig'], unique=True, primary_key=True)),
            ('domains', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('nodes', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('edges', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('ratio', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('seed', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'random', ['RandomConfig'])


    def backwards(self, orm):
        # Deleting model 'RandomConfig'
        db.delete_table(u'random_randomconfig')


    models = {
        u'acquisition.acquisitionsessionconfig': {
            'Meta': {'ordering': "['created']", 'object_name': 'AcquisitionSessionConfig'},
            'completed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'graph': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'started': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'temporary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'thumbnail': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'thumbnail_background': ('django.db.models.fields.CharField', [], {'max_length': '7', 'null': 'True', 'blank': 'True'})
        },
        u'acquisition.datacollectorconfig': {
            'Meta': {'object_name': 'DataCollectorConfig'},
            'completed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'configurator': ('django.db.models.fields.CharField', [], {'max_length': '44'}),
            'graph': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'output': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_acquisition.datacollectorconfig_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'result_id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'running_instance_id': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'session_config': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'collectors'", 'to': u"orm['acquisition.AcquisitionSessionConfig']"}),
            'started': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'random.randomconfig': {
            'Meta': {'object_name': 'RandomConfig', '_ormbases': [u'acquisition.DataCollectorConfig']},
            u'datacollectorconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['acquisition.DataCollectorConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'domains': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'edges': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'nodes': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'ratio': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'seed': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['random']