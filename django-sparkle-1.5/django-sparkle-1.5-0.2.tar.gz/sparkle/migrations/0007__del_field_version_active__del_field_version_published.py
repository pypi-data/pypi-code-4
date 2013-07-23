# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.utils import timezone

safe_default = datetime.datetime(1970, 1, 1, 0, 0, tzinfo=timezone.utc)

class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Version.active'
        db.delete_column(u'sparkle_version', 'active')

        # Deleting field 'Version.published'
        db.delete_column(u'sparkle_version', 'published')



    def backwards(self, orm):
        # Adding field 'Version.active'
        db.add_column(u'sparkle_version', 'active',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Version.published'
        db.add_column(u'sparkle_version', 'published',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=safe_default, blank=True),
                      keep_default=False)


    models = {
        u'sparkle.application': {
            'Meta': {'object_name': 'Application'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'})
        },
        u'sparkle.systemprofilereport': {
            'Meta': {'object_name': 'SystemProfileReport'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'})
        },
        u'sparkle.systemprofilereportrecord': {
            'Meta': {'object_name': 'SystemProfileReportRecord'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'report': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sparkle.SystemProfileReport']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        u'sparkle.version': {
            'Meta': {'object_name': 'Version'},
            'application': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sparkle.Application']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'dsa_signature': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'minimum_system_version': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'publish_date': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'null': 'True'}),
            'release_notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'short_version': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'update': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['sparkle']