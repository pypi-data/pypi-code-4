# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CiProject'
        db.create_table('ci_ciproject', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('branch', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('test_commands', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('ci', ['CiProject'])

        # Adding unique constraint on 'CiProject', fields ['name', 'branch']
        db.create_unique('ci_ciproject', ['name', 'branch'])

        # Adding M2M table for field dependancies on 'CiProject'
        db.create_table('ci_ciproject_dependancies', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_ciproject', models.ForeignKey(orm['ci.ciproject'], null=False)),
            ('to_ciproject', models.ForeignKey(orm['ci.ciproject'], null=False))
        ))
        db.create_unique('ci_ciproject_dependancies', ['from_ciproject_id', 'to_ciproject_id'])

        # Adding model 'TestModule'
        db.create_table('ci_testmodule', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('ci', ['TestModule'])

        # Adding model 'TestRun'
        db.create_table('ci_testrun', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ci.CiProject'])),
            ('module', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ci.TestModule'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('error', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('ci', ['TestRun'])


    def backwards(self, orm):
        # Removing unique constraint on 'CiProject', fields ['name', 'branch']
        db.delete_unique('ci_ciproject', ['name', 'branch'])

        # Deleting model 'CiProject'
        db.delete_table('ci_ciproject')

        # Removing M2M table for field dependancies on 'CiProject'
        db.delete_table('ci_ciproject_dependancies')

        # Deleting model 'TestModule'
        db.delete_table('ci_testmodule')

        # Deleting model 'TestRun'
        db.delete_table('ci_testrun')


    models = {
        'ci.ciproject': {
            'Meta': {'unique_together': "(('name', 'branch'),)", 'object_name': 'CiProject'},
            'branch': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'dependancies': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'dependancies_rel_+'", 'blank': 'True', 'to': "orm['ci.CiProject']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
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