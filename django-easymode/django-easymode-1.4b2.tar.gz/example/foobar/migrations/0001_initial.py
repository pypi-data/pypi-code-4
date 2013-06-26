# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Foo'
        db.create_table('foobar_foo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bar', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('barstool', self.gf('django.db.models.fields.TextField')(max_length=4)),
            ('website', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('city_en-us', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('city_de', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('city_en', self.gf('django.db.models.fields.CharField')(max_length=40, null=True)),
            ('date_en-us', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('date_de', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('date_en', self.gf('django.db.models.fields.DateField')(null=True)),
        ))
        db.send_create_signal('foobar', ['Foo'])

        # Adding model 'Bar'
        db.create_table('foobar_bar', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('foo', self.gf('django.db.models.fields.related.ForeignKey')(related_name='bars', to=orm['foobar.Foo'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal('foobar', ['Bar'])

        # Adding model 'Baz'
        db.create_table('foobar_baz', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('baz', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('independancy_level', self.gf('django.db.models.fields.IntegerField')()),
            ('kind', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('foobar', ['Baz'])


    def backwards(self, orm):
        
        # Deleting model 'Foo'
        db.delete_table('foobar_foo')

        # Deleting model 'Bar'
        db.delete_table('foobar_bar')

        # Deleting model 'Baz'
        db.delete_table('foobar_baz')


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
        }
    }

    complete_apps = ['foobar']
