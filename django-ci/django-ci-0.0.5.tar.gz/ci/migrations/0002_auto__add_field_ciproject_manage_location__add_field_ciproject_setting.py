# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'CiProject.manage_location'
        db.add_column('ci_ciproject', 'manage_location',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)

        # Adding field 'CiProject.settings_location'
        db.add_column('ci_ciproject', 'settings_location',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'CiProject.manage_location'
        db.delete_column('ci_ciproject', 'manage_location')

        # Deleting field 'CiProject.settings_location'
        db.delete_column('ci_ciproject', 'settings_location')


    models = {
        'ci.ciproject': {
            'Meta': {'unique_together': "(('name', 'branch'),)", 'object_name': 'CiProject'},
            'branch': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'dependancies': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'dependancies_rel_+'", 'blank': 'True', 'to': "orm['ci.CiProject']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manage_location': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'settings_location': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'test_commands': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'ci.testmodule': {
            'Meta': {'ordering': "('name',)", 'object_name': 'TestModule'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'ci.testrun': {
            'Meta': {'ordering': "('module', 'name')", 'object_name': 'TestRun'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'error': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ci.TestModule']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ci.CiProject']"}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['ci']