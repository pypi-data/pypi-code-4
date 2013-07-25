# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Stream.name'
        db.add_column(u'tt_streams_stream', 'name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=250),
                      keep_default=False)

        # Adding field 'Stream.summary'
        db.add_column(u'tt_streams_stream', 'summary',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Stream.name'
        db.delete_column(u'tt_streams_stream', 'name')

        # Deleting field 'Stream.summary'
        db.delete_column(u'tt_streams_stream', 'summary')


    models = {
        u'tt_streams.stream': {
            'Meta': {'object_name': 'Stream'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'summary': ('django.db.models.fields.TextField', [], {})
        },
        u'tt_streams.streamitem': {
            'Meta': {'object_name': 'StreamItem'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {}),
            'stream': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'items'", 'to': u"orm['tt_streams.Stream']"})
        }
    }

    complete_apps = ['tt_streams']