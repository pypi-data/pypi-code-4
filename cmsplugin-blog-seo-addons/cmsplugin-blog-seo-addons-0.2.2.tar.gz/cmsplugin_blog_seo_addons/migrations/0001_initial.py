# flake8: noqa
# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'EntrySEOAddon'
        db.create_table(u'cmsplugin_blog_seo_addons_entryseoaddon', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('entry', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cmsplugin_blog.Entry'])),
        ))
        db.send_create_signal(u'cmsplugin_blog_seo_addons', ['EntrySEOAddon'])

        # Adding model 'EntrySEOAddonTranslation'
        db.create_table(u'cmsplugin_blog_seo_addons_entryseoaddontranslation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('meta_description', self.gf('django.db.models.fields.TextField')(max_length=512, blank=True)),
            ('entryseoaddon', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cmsplugin_blog_seo_addons.EntrySEOAddon'])),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=5)),
        ))
        db.send_create_signal(u'cmsplugin_blog_seo_addons', ['EntrySEOAddonTranslation'])


    def backwards(self, orm):
        # Deleting model 'EntrySEOAddon'
        db.delete_table(u'cmsplugin_blog_seo_addons_entryseoaddon')

        # Deleting model 'EntrySEOAddonTranslation'
        db.delete_table(u'cmsplugin_blog_seo_addons_entryseoaddontranslation')


    models = {
        'cms.placeholder': {
            'Meta': {'object_name': 'Placeholder'},
            'default_width': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slot': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
        },
        u'cmsplugin_blog.entry': {
            'Meta': {'ordering': "('-pub_date',)", 'object_name': 'Entry'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'placeholders': ('djangocms_utils.fields.M2MPlaceholderField', [], {'to': "orm['cms.Placeholder']", 'symmetrical': 'False'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'tags': ('tagging.fields.TagField', [], {})
        },
        u'cmsplugin_blog_seo_addons.entryseoaddon': {
            'Meta': {'object_name': 'EntrySEOAddon'},
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cmsplugin_blog.Entry']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'cmsplugin_blog_seo_addons.entryseoaddontranslation': {
            'Meta': {'object_name': 'EntrySEOAddonTranslation'},
            'entryseoaddon': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cmsplugin_blog_seo_addons.EntrySEOAddon']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'meta_description': ('django.db.models.fields.TextField', [], {'max_length': '512', 'blank': 'True'})
        }
    }

    complete_apps = ['cmsplugin_blog_seo_addons']
