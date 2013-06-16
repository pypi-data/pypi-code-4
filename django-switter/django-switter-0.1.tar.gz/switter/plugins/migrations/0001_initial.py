# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SwitterTweets'
        db.create_table('cmsplugin_swittertweets', (
            ('cmsplugin_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cms.CMSPlugin'], unique=True, primary_key=True)),
            ('header', self.gf('django.db.models.fields.CharField')(default='Latest Tweets', max_length=255, blank=True)),
            ('query_type', self.gf('django.db.models.fields.CharField')(default='user_timeline', max_length=255)),
            ('twitter_id', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
            ('search_query', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
            ('show_retweets', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('show_replies', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('count', self.gf('django.db.models.fields.IntegerField')(default=3)),
            ('render_template', self.gf('django.db.models.fields.CharField')(default='cms/plugins/switter/default.html', max_length=255)),
        ))
        db.send_create_signal('plugins', ['SwitterTweets'])


    def backwards(self, orm):
        # Deleting model 'SwitterTweets'
        db.delete_table('cmsplugin_swittertweets')


    models = {
        'cms.cmsplugin': {
            'Meta': {'object_name': 'CMSPlugin'},
            'changed_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 6, 15, 0, 0)'}),
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
        'plugins.swittertweets': {
            'Meta': {'object_name': 'SwitterTweets', 'db_table': "'cmsplugin_swittertweets'", '_ormbases': ['cms.CMSPlugin']},
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'count': ('django.db.models.fields.IntegerField', [], {'default': '3'}),
            'header': ('django.db.models.fields.CharField', [], {'default': "'Latest Tweets'", 'max_length': '255', 'blank': 'True'}),
            'query_type': ('django.db.models.fields.CharField', [], {'default': "'user_timeline'", 'max_length': '255'}),
            'render_template': ('django.db.models.fields.CharField', [], {'default': "'cms/plugins/switter/default.html'", 'max_length': '255'}),
            'search_query': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'show_replies': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'show_retweets': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'twitter_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'})
        }
    }

    complete_apps = ['plugins']