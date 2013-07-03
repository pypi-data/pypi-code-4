# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'HTMLSitemap'
        db.create_table('jmbo_sitemap_htmlsitemap', (
            ('preferences_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['preferences.Preferences'], unique=True, primary_key=True)),
            ('content', self.gf('ckeditor.fields.RichTextField')(null=True, blank=True)),
            ('draft', self.gf('ckeditor.fields.RichTextField')(null=True, blank=True)),
        ))
        db.send_create_signal('jmbo_sitemap', ['HTMLSitemap'])


    def backwards(self, orm):
        # Deleting model 'HTMLSitemap'
        db.delete_table('jmbo_sitemap_htmlsitemap')


    models = {
        'jmbo_sitemap.htmlsitemap': {
            'Meta': {'object_name': 'HTMLSitemap', '_ormbases': ['preferences.Preferences']},
            'content': ('ckeditor.fields.RichTextField', [], {'null': 'True', 'blank': 'True'}),
            'draft': ('ckeditor.fields.RichTextField', [], {'null': 'True', 'blank': 'True'}),
            'preferences_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['preferences.Preferences']", 'unique': 'True', 'primary_key': 'True'})
        },
        'preferences.preferences': {
            'Meta': {'object_name': 'Preferences'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['sites.Site']", 'null': 'True', 'blank': 'True'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['jmbo_sitemap']