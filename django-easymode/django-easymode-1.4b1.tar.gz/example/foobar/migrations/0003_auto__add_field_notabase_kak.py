# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'NotABase.kak'
        db.add_column('foobar_notabase', 'kak', self.gf('django.db.models.fields.related.OneToOneField')(default=1, related_name='kaks', unique=True, to=orm['foobar.Baz']), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'NotABase.kak'
        db.delete_column('foobar_notabase', 'kak_id')


    models = {
        'foobar.bar': {
            'Meta': {'object_name': 'Bar'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'foo': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bars'", 'to': "orm['foobar.Foo']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'foobar.baz': {
            'Meta': {'object_name': 'Baz'},
            'baz': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'independancy_level': ('django.db.models.fields.IntegerField', [], {}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'foobar.foo': {
            'Meta': {'object_name': 'Foo'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'bar': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'barstool': ('django.db.models.fields.TextField', [], {'max_length': '4'}),
            'city_de': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'city_en': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True'}),
            'city_en-us': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'date_de': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_en': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'date_en-us': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'foobar.notabase': {
            'Meta': {'object_name': 'NotABase'},
            'extra': ('django.db.models.fields.CharField', [], {'max_length': '344'}),
            'hitehre': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['foobar.Baz']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kak': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'kaks'", 'unique': 'True', 'to': "orm['foobar.Baz']"}),
            'situp': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['foobar']
