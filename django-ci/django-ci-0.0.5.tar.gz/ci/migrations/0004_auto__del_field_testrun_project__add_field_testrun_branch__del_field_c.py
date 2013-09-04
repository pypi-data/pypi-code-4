# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'CiBranch', fields ['project', 'branch']
        db.delete_unique('ci_cibranch', ['project_id', 'branch'])

        # Deleting field 'TestRun.project'
        db.delete_column('ci_testrun', 'project_id')

        # Adding field 'TestRun.branch'
        db.add_column('ci_testrun', 'branch',
                      self.gf('django.db.models.fields.related.ForeignKey')(default='master', to=orm['ci.CiBranch']),
                      keep_default=False)

        # Deleting field 'CiBranch.branch'
        db.delete_column('ci_cibranch', 'branch')

        # Adding field 'CiBranch.name'
        db.add_column('ci_cibranch', 'name',
                      self.gf('django.db.models.fields.CharField')(default='master', max_length=50),
                      keep_default=False)

        # Adding unique constraint on 'CiBranch', fields ['project', 'name']
        db.create_unique('ci_cibranch', ['project_id', 'name'])


    def backwards(self, orm):
        # Removing unique constraint on 'CiBranch', fields ['project', 'name']
        db.delete_unique('ci_cibranch', ['project_id', 'name'])


        # User chose to not deal with backwards NULL issues for 'TestRun.project'
        raise RuntimeError("Cannot reverse this migration. 'TestRun.project' and its values cannot be restored.")
        # Deleting field 'TestRun.branch'
        db.delete_column('ci_testrun', 'branch_id')


        # User chose to not deal with backwards NULL issues for 'CiBranch.branch'
        raise RuntimeError("Cannot reverse this migration. 'CiBranch.branch' and its values cannot be restored.")
        # Deleting field 'CiBranch.name'
        db.delete_column('ci_cibranch', 'name')

        # Adding unique constraint on 'CiBranch', fields ['project', 'branch']
        db.create_unique('ci_cibranch', ['project_id', 'branch'])


    models = {
        'ci.cibranch': {
            'Meta': {'unique_together': "(('project', 'name'),)", 'object_name': 'CiBranch'},
            'celery_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'dependancies': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ci.CiProject']"})
        },
        'ci.ciproject': {
            'Meta': {'object_name': 'CiProject'},
            'dependancies': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manage_location': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'settings_module': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
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