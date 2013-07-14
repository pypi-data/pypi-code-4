# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Version.version'
        db.alter_column(u'pypi_version', 'version', self.gf('django.db.models.fields.CharField')(max_length=40))

    def backwards(self, orm):

        # Changing field 'Version.version'
        db.alter_column(u'pypi_version', 'version', self.gf('django.db.models.fields.CharField')(max_length=20))

    models = {
        u'pypi.package': {
            'Meta': {'object_name': 'Package'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'pypi.release': {
            'Meta': {'ordering': "('version', 'upload_time')", 'unique_together': "(('version', 'upload_time'),)", 'object_name': 'Release'},
            'comment_text': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'downloads': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'has_sig': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'md5_digest': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'packagetype': ('django.db.models.fields.CharField', [], {'max_length': '13'}),
            'python_version': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'size': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'upload_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'releases'", 'to': u"orm['pypi.Version']"})
        },
        u'pypi.version': {
            'Meta': {'unique_together': "(('package', 'version'),)", 'object_name': 'Version'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'versions'", 'to': u"orm['pypi.Package']"}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        }
    }

    complete_apps = ['pypi']