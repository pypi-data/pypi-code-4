# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SearchQuery'
        db.create_table(u'search_statistic_searchquery', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('query', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255, db_index=True)),
            ('confirm', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'search_statistic', ['SearchQuery'])

        # Adding model 'Visit'
        db.create_table(u'search_statistic_visit', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('query', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['search_statistic.SearchQuery'])),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('content_type', self.gf('django.db.models.fields.CharField')(max_length=127, null=True, blank=True)),
            ('object_pk', self.gf('django.db.models.fields.IntegerField')(default=None, null=True)),
            ('search_engine', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('amount', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'search_statistic', ['Visit'])


    def backwards(self, orm):
        # Deleting model 'SearchQuery'
        db.delete_table(u'search_statistic_searchquery')

        # Deleting model 'Visit'
        db.delete_table(u'search_statistic_visit')


    models = {
        u'search_statistic.searchquery': {
            'Meta': {'object_name': 'SearchQuery'},
            'confirm': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'query': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'})
        },
        u'search_statistic.visit': {
            'Meta': {'ordering': "['-timestamp']", 'object_name': 'Visit'},
            'amount': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'content_type': ('django.db.models.fields.CharField', [], {'max_length': '127', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_pk': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'query': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['search_statistic.SearchQuery']"}),
            'search_engine': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['search_statistic']