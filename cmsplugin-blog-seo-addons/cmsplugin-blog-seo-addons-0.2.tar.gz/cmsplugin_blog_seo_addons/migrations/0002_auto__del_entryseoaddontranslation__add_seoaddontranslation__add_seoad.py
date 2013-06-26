# flake8: noqa
# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'EntrySEOAddonTranslation'
        db.delete_table(u'cmsplugin_blog_seo_addons_entryseoaddontranslation')

        # Adding model 'SEOAddonTranslation'
        db.create_table('cmsplugin_blog_seo_addons_seoaddontranslation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('meta_description', self.gf('django.db.models.fields.TextField')(max_length=512, blank=True)),
            ('seoaddon', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cmsplugin_blog_seo_addons.SEOAddon'])),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=5)),
        ))
        db.send_create_signal('cmsplugin_blog_seo_addons', ['SEOAddonTranslation'])

        # Adding model 'SEOAddon'
        db.create_table('cmsplugin_blog_seo_addons_seoaddon', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('cmsplugin_blog_seo_addons', ['SEOAddon'])

        # Adding field 'EntrySEOAddon.seoaddon'
        db.add_column('cmsplugin_blog_seo_addons_entryseoaddon', 'seoaddon',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cmsplugin_blog_seo_addons.SEOAddon'], null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding model 'EntrySEOAddonTranslation'
        db.create_table(u'cmsplugin_blog_seo_addons_entryseoaddontranslation', (
            ('meta_description', self.gf('django.db.models.fields.TextField')(max_length=512, blank=True)),
            ('entryseoaddon', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cmsplugin_blog_seo_addons.EntrySEOAddon'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=5)),
        ))
        db.send_create_signal(u'cmsplugin_blog_seo_addons', ['EntrySEOAddonTranslation'])

        # Deleting model 'SEOAddonTranslation'
        db.delete_table('cmsplugin_blog_seo_addons_seoaddontranslation')

        # Deleting model 'SEOAddon'
        db.delete_table('cmsplugin_blog_seo_addons_seoaddon')

        # Deleting field 'EntrySEOAddon.seoaddon'
        db.delete_column('cmsplugin_blog_seo_addons_entryseoaddon', 'seoaddon_id')


    models = {
        'cms.placeholder': {
            'Meta': {'object_name': 'Placeholder'},
            'default_width': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slot': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'cmsplugin_blog.entry': {
            'Meta': {'ordering': "('-pub_date',)", 'object_name': 'Entry'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'placeholders': ('djangocms_utils.fields.M2MPlaceholderField', [], {'to': "orm['cms.Placeholder']", 'symmetrical': 'False'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'tags': ('tagging.fields.TagField', [], {})
        },
        'cmsplugin_blog_seo_addons.entryseoaddon': {
            'Meta': {'object_name': 'EntrySEOAddon'},
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cmsplugin_blog.Entry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'seoaddon': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cmsplugin_blog_seo_addons.SEOAddon']", 'null': 'True', 'blank': 'True'})
        },
        'cmsplugin_blog_seo_addons.seoaddon': {
            'Meta': {'object_name': 'SEOAddon'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'cmsplugin_blog_seo_addons.seoaddontranslation': {
            'Meta': {'object_name': 'SEOAddonTranslation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'meta_description': ('django.db.models.fields.TextField', [], {'max_length': '512', 'blank': 'True'}),
            'seoaddon': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cmsplugin_blog_seo_addons.SEOAddon']"})
        }
    }

    complete_apps = ['cmsplugin_blog_seo_addons']
