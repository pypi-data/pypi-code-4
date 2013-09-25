# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Link'
        db.create_table(u'django_relinking_link', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('keys', self.gf('django.db.models.fields.TextField')()),
            ('content_type', self.gf('django.db.models.fields.CharField')(default=None, max_length=255, null=True)),
            ('object_pk', self.gf('django.db.models.fields.CharField')(default=None, max_length=255, null=True)),
            ('direct_link', self.gf('django.db.models.fields.CharField')(default=None, max_length=255, null=True)),
            ('target', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'django_relinking', ['Link'])


    def backwards(self, orm):
        # Deleting model 'Link'
        db.delete_table(u'django_relinking_link')


    models = {
        u'django_relinking.link': {
            'Meta': {'ordering': "['priority']", 'object_name': 'Link'},
            'content_type': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True'}),
            'direct_link': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keys': ('django.db.models.fields.TextField', [], {}),
            'object_pk': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'target': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['django_relinking']