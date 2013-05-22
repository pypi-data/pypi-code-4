# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'LogEntry'
        db.create_table(u'memento_logentry', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='log_entries', to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('severity', self.gf('django.db.models.fields.IntegerField')()),
            ('last_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'memento', ['LogEntry'])

        # Adding model 'Event'
        db.create_table(u'memento_event', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('entry', self.gf('django.db.models.fields.related.ForeignKey')(related_name='events', to=orm['memento.LogEntry'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'memento', ['Event'])


    def backwards(self, orm):
        # Deleting model 'LogEntry'
        db.delete_table(u'memento_logentry')

        # Deleting model 'Event'
        db.delete_table(u'memento_event')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'memento.event': {
            'Meta': {'ordering': "('entry', '-timestamp')", 'object_name': 'Event'},
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'events'", 'to': u"orm['memento.LogEntry']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'memento.logentry': {
            'Meta': {'ordering': "('-last_timestamp',)", 'object_name': 'LogEntry'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'log_entries'", 'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'severity': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['memento']