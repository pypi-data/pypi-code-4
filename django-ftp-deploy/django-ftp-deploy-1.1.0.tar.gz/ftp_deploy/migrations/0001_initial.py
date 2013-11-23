# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Service'
        db.create_table(u'ftp_deploy_service', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ftp_host', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('ftp_username', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('ftp_password', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('ftp_path', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('repo_source', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('repo_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('repo_slug_name', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('repo_branch', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('repo_hook', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('secret_key', self.gf('django.db.models.fields.CharField')(default='ZTPBHR7OK0KglXN1w3pIQV2oSSSED3', unique=True, max_length=30)),
            ('status', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('status_message', self.gf('django.db.models.fields.TextField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'ftp_deploy', ['Service'])

        # Adding model 'Log'
        db.create_table(u'ftp_deploy_log', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ftp_deploy.Service'], blank=True)),
            ('payload', self.gf('django.db.models.fields.TextField')()),
            ('user', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('status', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('status_message', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('skip', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'ftp_deploy', ['Log'])


    def backwards(self, orm):
        # Deleting model 'Service'
        db.delete_table(u'ftp_deploy_service')

        # Deleting model 'Log'
        db.delete_table(u'ftp_deploy_log')


    models = {
        u'ftp_deploy.log': {
            'Meta': {'ordering': "('-created',)", 'object_name': 'Log'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payload': ('django.db.models.fields.TextField', [], {}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ftp_deploy.Service']", 'blank': 'True'}),
            'skip': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'status_message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'ftp_deploy.service': {
            'Meta': {'object_name': 'Service'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'ftp_host': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ftp_password': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'ftp_path': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ftp_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'repo_branch': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'repo_hook': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'repo_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'repo_slug_name': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'repo_source': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'secret_key': ('django.db.models.fields.CharField', [], {'default': "'ohPqA5RjE8cxO7dtL5yWe04qZjfXEA'", 'unique': 'True', 'max_length': '30'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'status_message': ('django.db.models.fields.TextField', [], {}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['ftp_deploy']