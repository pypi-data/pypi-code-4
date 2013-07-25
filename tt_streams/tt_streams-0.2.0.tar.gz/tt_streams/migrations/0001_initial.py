# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Stream'
        db.create_table(u'tt_streams_stream', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
        ))
        db.send_create_signal(u'tt_streams', ['Stream'])

        # Adding model 'StreamItem'
        db.create_table(u'tt_streams_streamitem', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('stream', self.gf('django.db.models.fields.related.ForeignKey')(related_name='items', to=orm['tt_streams.Stream'])),
            ('pub_date', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'tt_streams', ['StreamItem'])


    def backwards(self, orm):
        # Deleting model 'Stream'
        db.delete_table(u'tt_streams_stream')

        # Deleting model 'StreamItem'
        db.delete_table(u'tt_streams_streamitem')


    models = {
        u'tt_streams.stream': {
            'Meta': {'object_name': 'Stream'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        u'tt_streams.streamitem': {
            'Meta': {'object_name': 'StreamItem'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {}),
            'stream': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'items'", 'to': u"orm['tt_streams.Stream']"})
        }
    }

    complete_apps = ['tt_streams']