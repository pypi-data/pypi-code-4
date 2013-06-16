# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CachedTweets'
        db.create_table('switter_cachedtweets', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('query_type', self.gf('django.db.models.fields.CharField')(default='user_timeline', max_length=255)),
            ('query_value', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
            ('cached_response', self.gf('django.db.models.fields.TextField')(default='{}', blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
        ))
        db.send_create_signal('switter', ['CachedTweets'])

        # Adding unique constraint on 'CachedTweets', fields ['query_type', 'query_value']
        db.create_unique('switter_cachedtweets', ['query_type', 'query_value'])


    def backwards(self, orm):
        # Removing unique constraint on 'CachedTweets', fields ['query_type', 'query_value']
        db.delete_unique('switter_cachedtweets', ['query_type', 'query_value'])

        # Deleting model 'CachedTweets'
        db.delete_table('switter_cachedtweets')


    models = {
        'switter.cachedtweets': {
            'Meta': {'unique_together': "(('query_type', 'query_value'),)", 'object_name': 'CachedTweets'},
            'cached_response': ('django.db.models.fields.TextField', [], {'default': "'{}'", 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'query_type': ('django.db.models.fields.CharField', [], {'default': "'user_timeline'", 'max_length': '255'}),
            'query_value': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'})
        }
    }

    complete_apps = ['switter']