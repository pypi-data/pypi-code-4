# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'Provider.notice'
        db.alter_column('smscoin_provider', 'notice', self.gf('django.db.models.fields.CharField')(max_length=512))


    def backwards(self, orm):
        
        # Changing field 'Provider.notice'
        db.alter_column('smscoin_provider', 'notice', self.gf('django.db.models.fields.CharField')(max_length=128))


    models = {
        'smscoin.provider': {
            'Meta': {'ordering': "('country', 'code')", 'object_name': 'Provider'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'country': ('django_countries.fields.CountryField', [], {'max_length': '2'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'notice': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'prefix': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'profit': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'rewrite': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'usd': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'vat': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['smscoin']
