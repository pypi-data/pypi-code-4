# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ThemeUserAgent'
        db.create_table('django_diazo_themeuseragent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('theme', self.gf('django.db.models.fields.related.ForeignKey')(related_name='useragent_strings', to=orm['django_diazo.Theme'])),
            ('pattern', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('allow', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('sort', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('django_diazo', ['ThemeUserAgent'])

        # Adding field 'Theme.sort'
        db.add_column('django_diazo_theme', 'sort',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'ThemeUserAgent'
        db.delete_table('django_diazo_themeuseragent')

        # Deleting field 'Theme.sort'
        db.delete_column('django_diazo_theme', 'sort')


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'django_diazo.compoundrule': {
            'Meta': {'object_name': 'CompoundRule', '_ormbases': ['django_diazo.Rule']},
            'prefix': ('django.db.models.fields.TextField', [], {}),
            'rule_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['django_diazo.Rule']", 'unique': 'True', 'primary_key': 'True'}),
            'rules': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'compound_rule'", 'blank': 'True', 'to': "orm['django_diazo.Rule']"}),
            'suffix': ('django.db.models.fields.TextField', [], {})
        },
        'django_diazo.rule': {
            'Meta': {'object_name': 'Rule'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'polymorphic_django_diazo.rule_set'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'root': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'django_diazo.singlerule': {
            'Meta': {'object_name': 'SingleRule', '_ormbases': ['django_diazo.Rule']},
            'rule': ('django.db.models.fields.TextField', [], {}),
            'rule_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['django_diazo.Rule']", 'unique': 'True', 'primary_key': 'True'})
        },
        'django_diazo.theme': {
            'Meta': {'object_name': 'Theme'},
            'builtin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'debug': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'prefix': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'rules': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'themes'", 'null': 'True', 'to': "orm['django_diazo.Rule']"}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sort': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'django_diazo.themeuseragent': {
            'Meta': {'object_name': 'ThemeUserAgent'},
            'allow': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pattern': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sort': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'theme': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'useragent_strings'", 'to': "orm['django_diazo.Theme']"})
        }
    }

    complete_apps = ['django_diazo']