# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FileSystem'
        db.create_table(u'projects_filesystem', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mount_point', self.gf('django.db.models.fields.CharField')(unique=True, max_length=2000)),
        ))
        db.send_create_signal(u'projects', ['FileSystem'])

        # Adding model 'Project'
        db.create_table(u'projects_project', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('file_system', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.FileSystem'])),
            ('directory', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'projects', ['Project'])

        # Adding unique constraint on 'Project', fields ['file_system', 'directory']
        db.create_unique(u'projects_project', ['file_system_id', 'directory'])


    def backwards(self, orm):
        # Removing unique constraint on 'Project', fields ['file_system', 'directory']
        db.delete_unique(u'projects_project', ['file_system_id', 'directory'])

        # Deleting model 'FileSystem'
        db.delete_table(u'projects_filesystem')

        # Deleting model 'Project'
        db.delete_table(u'projects_project')


    models = {
        u'projects.filesystem': {
            'Meta': {'object_name': 'FileSystem'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mount_point': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '2000'})
        },
        u'projects.project': {
            'Meta': {'unique_together': "(('file_system', 'directory'),)", 'object_name': 'Project'},
            'directory': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'file_system': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.FileSystem']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['projects']