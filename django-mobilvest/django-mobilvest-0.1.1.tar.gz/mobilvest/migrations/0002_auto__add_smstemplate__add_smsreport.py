# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SMSTemplate'
        db.create_table('mobilvest_smstemplate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('text', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('mobilvest', ['SMSTemplate'])

        # Adding model 'SMSReport'
        db.create_table('mobilvest_smsreport', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 12, 12, 0, 0), auto_now_add=True, blank=True)),
            ('sms_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('response_status', self.gf('django.db.models.fields.CharField')(default='send', max_length=150)),
            ('mobile_phone', self.gf('django.db.models.fields.CharField')(max_length=15, null=True, blank=True)),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('error', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('mobilvest', ['SMSReport'])


    def backwards(self, orm):
        # Deleting model 'SMSTemplate'
        db.delete_table('mobilvest_smstemplate')

        # Deleting model 'SMSReport'
        db.delete_table('mobilvest_smsreport')


    models = {
        'mobilvest.smsreport': {
            'Meta': {'object_name': 'SMSReport'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 12, 12, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'error': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mobile_phone': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'response_status': ('django.db.models.fields.CharField', [], {'default': "'send'", 'max_length': '150'}),
            'sms_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'mobilvest.smstemplate': {
            'Meta': {'object_name': 'SMSTemplate'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'text': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['mobilvest']