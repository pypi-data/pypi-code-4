# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Queue'
        db.create_table(u'django_queue_mailer_queue', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('to_address', self.gf('django.db.models.fields.EmailField')(max_length=250)),
            ('bcc_address', self.gf('django.db.models.fields.EmailField')(max_length=250, blank=True)),
            ('from_address', self.gf('django.db.models.fields.EmailField')(max_length=250)),
            ('content', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('html_content', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('app', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('deferred', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_attempt', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'django_queue_mailer', ['Queue'])

        # Adding model 'Attachment'
        db.create_table(u'django_queue_mailer_attachment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('file_attachment', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['django_queue_mailer.Queue'], null=True, blank=True)),
        ))
        db.send_create_signal(u'django_queue_mailer', ['Attachment'])

        # Adding model 'Log'
        db.create_table(u'django_queue_mailer_log', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('message_id', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('to_address', self.gf('django.db.models.fields.EmailField')(max_length=250)),
            ('bcc_address', self.gf('django.db.models.fields.EmailField')(max_length=250, blank=True)),
            ('from_address', self.gf('django.db.models.fields.EmailField')(max_length=250)),
            ('content', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('html_content', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('app', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('sent', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'django_queue_mailer', ['Log'])


    def backwards(self, orm):
        # Deleting model 'Queue'
        db.delete_table(u'django_queue_mailer_queue')

        # Deleting model 'Attachment'
        db.delete_table(u'django_queue_mailer_attachment')

        # Deleting model 'Log'
        db.delete_table(u'django_queue_mailer_log')


    models = {
        u'django_queue_mailer.attachment': {
            'Meta': {'object_name': 'Attachment'},
            'email': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['django_queue_mailer.Queue']", 'null': 'True', 'blank': 'True'}),
            'file_attachment': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'django_queue_mailer.log': {
            'Meta': {'object_name': 'Log'},
            'app': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'bcc_address': ('django.db.models.fields.EmailField', [], {'max_length': '250', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'from_address': ('django.db.models.fields.EmailField', [], {'max_length': '250'}),
            'html_content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message_id': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'sent': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'to_address': ('django.db.models.fields.EmailField', [], {'max_length': '250'})
        },
        u'django_queue_mailer.queue': {
            'Meta': {'object_name': 'Queue'},
            'app': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'bcc_address': ('django.db.models.fields.EmailField', [], {'max_length': '250', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deferred': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'from_address': ('django.db.models.fields.EmailField', [], {'max_length': '250'}),
            'html_content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_attempt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'to_address': ('django.db.models.fields.EmailField', [], {'max_length': '250'})
        }
    }

    complete_apps = ['django_queue_mailer']