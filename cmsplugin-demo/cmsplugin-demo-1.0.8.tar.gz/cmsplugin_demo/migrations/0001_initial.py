# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Demo'
        db.create_table('cmsplugin_demo', (
            ('cmsplugin_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cms.CMSPlugin'], unique=True, primary_key=True)),
            ('form_name', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
            ('form_layout', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('site_email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('thanks', self.gf('django.db.models.fields.TextField')(default=u'Thank you for your message.', max_length=200)),
            ('submit', self.gf('django.db.models.fields.CharField')(default=u'Submit', max_length=30)),
            ('spam_protection_method', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('akismet_api_key', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('recaptcha_public_key', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('recaptcha_private_key', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('recaptcha_theme', self.gf('django.db.models.fields.CharField')(default='clean', max_length=20)),
        ))
        db.send_create_signal('cmsplugin_demo', ['Demo'])


    def backwards(self, orm):
        # Deleting model 'Demo'
        db.delete_table('cmsplugin_demo')


    models = {
        'cms.cmsplugin': {
            'Meta': {'object_name': 'CMSPlugin'},
            'changed_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 11, 4, 0, 0)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.CMSPlugin']", 'null': 'True', 'blank': 'True'}),
            'placeholder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Placeholder']", 'null': 'True'}),
            'plugin_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'cms.placeholder': {
            'Meta': {'object_name': 'Placeholder'},
            'default_width': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slot': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'cmsplugin_demo.demo': {
            'Meta': {'object_name': 'Demo', 'db_table': "'cmsplugin_demo'"},
            'akismet_api_key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'form_layout': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'form_name': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'recaptcha_private_key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'recaptcha_public_key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'recaptcha_theme': ('django.db.models.fields.CharField', [], {'default': "'clean'", 'max_length': '20'}),
            'site_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'spam_protection_method': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'submit': ('django.db.models.fields.CharField', [], {'default': "u'Submit'", 'max_length': '30'}),
            'thanks': ('django.db.models.fields.TextField', [], {'default': "u'Thank you for your message.'", 'max_length': '200'})
        }
    }

    complete_apps = ['cmsplugin_demo']