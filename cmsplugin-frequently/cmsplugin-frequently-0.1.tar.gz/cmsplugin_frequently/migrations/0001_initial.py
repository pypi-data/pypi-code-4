# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FrequentlyEntryCategoryPlugin'
        db.create_table('cmsplugin_frequentlyentrycategoryplugin', (
            ('cmsplugin_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cms.CMSPlugin'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('cmsplugin_frequently', ['FrequentlyEntryCategoryPlugin'])

        # Adding M2M table for field categories on 'FrequentlyEntryCategoryPlugin'
        m2m_table_name = db.shorten_name('cmsplugin_frequently_frequentlyentrycategoryplugin_categories')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('frequentlyentrycategoryplugin', models.ForeignKey(orm['cmsplugin_frequently.frequentlyentrycategoryplugin'], null=False)),
            ('entrycategory', models.ForeignKey(orm['frequently.entrycategory'], null=False))
        ))
        db.create_unique(m2m_table_name, ['frequentlyentrycategoryplugin_id', 'entrycategory_id'])


    def backwards(self, orm):
        # Deleting model 'FrequentlyEntryCategoryPlugin'
        db.delete_table('cmsplugin_frequentlyentrycategoryplugin')

        # Removing M2M table for field categories on 'FrequentlyEntryCategoryPlugin'
        db.delete_table(db.shorten_name('cmsplugin_frequentlyentrycategoryplugin_categories'))


    models = {
        'cms.cmsplugin': {
            'Meta': {'object_name': 'CMSPlugin'},
            'changed_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 11, 23, 0, 0)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.CMSPlugin']", 'null': 'True', 'blank': 'True'}),
            'placeholder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Placeholder']", 'null': 'True'}),
            'plugin_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'cms.placeholder': {
            'Meta': {'object_name': 'Placeholder'},
            'default_width': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slot': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'cmsplugin_frequently.frequentlyentrycategoryplugin': {
            'Meta': {'object_name': 'FrequentlyEntryCategoryPlugin', 'db_table': "'cmsplugin_frequentlyentrycategoryplugin'", '_ormbases': ['cms.CMSPlugin']},
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'cmsplugin_frequently_entrycategoryplugins'", 'symmetrical': 'False', 'to': "orm['frequently.EntryCategory']"}),
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'})
        },
        'frequently.entrycategory': {
            'Meta': {'ordering': "['fixed_position', 'name']", 'object_name': 'EntryCategory'},
            'fixed_position': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_rank': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        }
    }

    complete_apps = ['cmsplugin_frequently']
