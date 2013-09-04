# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'CiProject', fields ['name', 'branch']
        db.delete_unique('ci_ciproject', ['name', 'branch'])

        # Adding model 'CommandGroup'
        db.create_table('ci_commandgroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ci.CiProject'])),
            ('branch', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('ci', ['CommandGroup'])

        # Adding model 'Command'
        db.create_table('ci_command', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ci.CommandGroup'])),
            ('ordering', self.gf('django.db.models.fields.SmallIntegerField')(default=100)),
            ('working_directory', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('commands', self.gf('django.db.models.fields.TextField')()),
            ('environment', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('ci', ['Command'])

        # Adding model 'CiBranch'
        db.create_table('ci_cibranch', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ci.CiProject'])),
            ('branch', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('dependancies', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('celery_id', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('ci', ['CiBranch'])

        # Adding unique constraint on 'CiBranch', fields ['project', 'branch']
        db.create_unique('ci_cibranch', ['project_id', 'branch'])

        # Deleting field 'CiProject.test_commands'
        db.delete_column('ci_ciproject', 'test_commands')

        # Deleting field 'CiProject.branch'
        db.delete_column('ci_ciproject', 'branch')

        # Deleting field 'CiProject.settings_location'
        db.delete_column('ci_ciproject', 'settings_location')

        # Adding field 'CiProject.dependancies'
        db.add_column('ci_ciproject', 'dependancies',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'CiProject.settings_module'
        db.add_column('ci_ciproject', 'settings_module',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255),
                      keep_default=False)

        # Removing M2M table for field dependancies on 'CiProject'
        db.delete_table('ci_ciproject_dependancies')


        # Changing field 'CiProject.manage_location'
        db.alter_column('ci_ciproject', 'manage_location', self.gf('django.db.models.fields.CharField')(default='', max_length=255))

    def backwards(self, orm):
        # Removing unique constraint on 'CiBranch', fields ['project', 'branch']
        db.delete_unique('ci_cibranch', ['project_id', 'branch'])

        # Deleting model 'CommandGroup'
        db.delete_table('ci_commandgroup')

        # Deleting model 'Command'
        db.delete_table('ci_command')

        # Deleting model 'CiBranch'
        db.delete_table('ci_cibranch')

        # Adding field 'CiProject.test_commands'
        db.add_column('ci_ciproject', 'test_commands',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'CiProject.branch'
        db.add_column('ci_ciproject', 'branch',
                      self.gf('django.db.models.fields.CharField')(default='master', max_length=50),
                      keep_default=False)

        # Adding field 'CiProject.settings_location'
        db.add_column('ci_ciproject', 'settings_location',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)

        # Deleting field 'CiProject.dependancies'
        db.delete_column('ci_ciproject', 'dependancies')

        # Deleting field 'CiProject.settings_module'
        db.delete_column('ci_ciproject', 'settings_module')

        # Adding M2M table for field dependancies on 'CiProject'
        db.create_table('ci_ciproject_dependancies', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_ciproject', models.ForeignKey(orm['ci.ciproject'], null=False)),
            ('to_ciproject', models.ForeignKey(orm['ci.ciproject'], null=False))
        ))
        db.create_unique('ci_ciproject_dependancies', ['from_ciproject_id', 'to_ciproject_id'])


        # Changing field 'CiProject.manage_location'
        db.alter_column('ci_ciproject', 'manage_location', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))
        # Adding unique constraint on 'CiProject', fields ['name', 'branch']
        db.create_unique('ci_ciproject', ['name', 'branch'])


    models = {
        'ci.cibranch': {
            'Meta': {'unique_together': "(('project', 'branch'),)", 'object_name': 'CiBranch'},
            'branch': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'celery_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'dependancies': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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