# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Photo'
        db.create_table('rgallery_photo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('origen', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('insert_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('capture_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('status', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('rgallery', ['Photo'])

        # Adding model 'Video'
        db.create_table('rgallery_video', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('video', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('origen', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('insert_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('capture_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('status', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('rgallery', ['Video'])


    def backwards(self, orm):
        # Deleting model 'Photo'
        db.delete_table('rgallery_photo')

        # Deleting model 'Video'
        db.delete_table('rgallery_video')


    models = {
        'rgallery.photo': {
            'Meta': {'object_name': 'Photo'},
            'capture_date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'insert_date': ('django.db.models.fields.DateTimeField', [], {}),
            'origen': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'rgallery.video': {
            'Meta': {'object_name': 'Video'},
            'capture_date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'insert_date': ('django.db.models.fields.DateTimeField', [], {}),
            'origen': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'video': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'})
        }
    }

    complete_apps = ['rgallery']