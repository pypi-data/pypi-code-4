# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Theme.rules'
        db.alter_column('django_diazo_theme', 'rules', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'Theme.prefix'
        db.alter_column('django_diazo_theme', 'prefix', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'Theme.name'
        db.alter_column('django_diazo_theme', 'name', self.gf('django.db.models.fields.CharField')(max_length=255))

    def backwards(self, orm):

        # Changing field 'Theme.rules'
        db.alter_column('django_diazo_theme', 'rules', self.gf('django.db.models.fields.TextField')())

        # Changing field 'Theme.prefix'
        db.alter_column('django_diazo_theme', 'prefix', self.gf('django.db.models.fields.TextField')())

        # Changing field 'Theme.name'
        db.alter_column('django_diazo_theme', 'name', self.gf('django.db.models.fields.TextField')())

    models = {
        'django_diazo.theme': {
            'Meta': {'object_name': 'Theme'},
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'prefix': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'rules': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        }
    }

    complete_apps = ['django_diazo']