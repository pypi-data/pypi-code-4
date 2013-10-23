# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Theme.rules'
        db.add_column('django_diazo_theme', 'rules',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Theme.prefix'
        db.add_column('django_diazo_theme', 'prefix',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Theme.rules'
        db.delete_column('django_diazo_theme', 'rules')

        # Deleting field 'Theme.prefix'
        db.delete_column('django_diazo_theme', 'prefix')


    models = {
        'django_diazo.theme': {
            'Meta': {'object_name': 'Theme'},
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'prefix': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'rules': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        }
    }

    complete_apps = ['django_diazo']