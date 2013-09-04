# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'CiProject.slug'
        db.add_column('ci_ciproject', 'slug',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50),
                      keep_default=False)

        # Adding field 'CiBranch.slug'
        db.add_column('ci_cibranch', 'slug',
                      self.gf('django.db.models.fields.SlugField')(default='', max_length=50),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'CiProject.slug'
        db.delete_column('ci_ciproject', 'slug')

        # Deleting field 'CiBranch.slug'
        db.delete_column('ci_cibranch', 'slug')


    models = {
        'ci.cibranch': {
            'Meta': {'unique_together': "(('project', 'name'),)", 'object_name': 'CiBranch'},
            'celery_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'dependancies': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ci.CiProject']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        'ci.ciproject': {
            'Meta': {'object_name': 'CiProject'},
            'dependancies': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manage_location': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'settings_module': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'ci.command': {
            'Meta': {'ordering': "('ordering',)", 'object_name': 'Command'},
            'commands': ('django.db.models.fields.TextField', [], {}),
            'environment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ordering': ('django.db.models.fields.SmallIntegerField', [], {'default': '100'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ci.CommandGroup']"}),
            'working_directory': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'ci.commandgroup': {
            'Meta': {'object_name': 'CommandGroup'},
            'branch': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ci.CiProject']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'ci.testmodule': {
            'Meta': {'ordering': "('name',)", 'object_name': 'TestModule'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'ci.testrun': {
            'Meta': {'ordering': "('module', 'name')", 'object_name': 'TestRun'},
            'branch': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ci.CiBranch']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'error': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ci.TestModule']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['ci']