# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Event'
        db.delete_table(u'memento_event')

        # Adding model 'LogEvent'
        db.create_table(u'memento_logevent', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('entry', self.gf('django.db.models.fields.related.ForeignKey')(related_name='events', to=orm['memento.LogEntry'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'memento', ['LogEvent'])


        # Changing field 'LogEntry.object_id'
        db.alter_column(u'memento_logentry', 'object_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True))

        # Changing field 'LogEntry.content_type'
        db.alter_column(u'memento_logentry', 'content_type_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['contenttypes.ContentType']))

    def backwards(self, orm):
        # Adding model 'Event'
        db.create_table(u'memento_event', (
            ('entry', self.gf('django.db.models.fields.related.ForeignKey')(related_name='events', to=orm['memento.LogEntry'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'memento', ['Event'])

        # Deleting model 'LogEvent'
        db.delete_table(u'memento_logevent')


        # User chose to not deal with backwards NULL issues for 'LogEntry.object_id'
        raise RuntimeError("Cannot reverse this migration. 'LogEntry.object_id' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'LogEntry.content_type'
        raise RuntimeError("Cannot reverse this migration. 'LogEntry.content_type' and its values cannot be restored.")

    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'memento.logentry': {
            'Meta': {'ordering': "('-last_timestamp',)", 'object_name': 'LogEntry'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'log_entries'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'severity': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        u'memento.logevent': {
            'Meta': {'ordering': "('entry', '-timestamp')", 'object_name': 'LogEvent'},
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'events'", 'to': u"orm['memento.LogEntry']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['memento']