# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Changing field 'ViddlerVideo.made_public_time'
        # db.alter_column('viddler_viddlervideo', 'made_public_time', self.gf('django.db.models.fields.DateTimeField')(null=True))
        db.delete_column('viddler_viddlervideo', 'made_public_time')
        db.add_column('viddler_viddlervideo', 'made_public_time',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

        # Changing field 'ViddlerVideo.upload_time'
        # db.alter_column('viddler_viddlervideo', 'upload_time', self.gf('django.db.models.fields.DateTimeField')())
        db.delete_column('viddler_viddlervideo', 'upload_time')
        db.add_column('viddler_viddlervideo', 'upload_time',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 10, 24, 0, 0)),
                      keep_default=False)


    def backwards(self, orm):

        # Changing field 'ViddlerVideo.made_public_time'
        # db.alter_column('viddler_viddlervideo', 'made_public_time', self.gf('django.db.models.fields.TimeField')(null=True))
        db.delete_column('viddler_viddlervideo', 'made_public_time')
        db.add_column('viddler_viddlervideo', 'made_public_time',
                      self.gf('django.db.models.fields.TimeField')(null=True, blank=True),
                      keep_default=False)

        # Changing field 'ViddlerVideo.upload_time'
        # db.alter_column('viddler_viddlervideo', 'upload_time', self.gf('django.db.models.fields.TimeField')())
        db.delete_column('viddler_viddlervideo', 'upload_time')
        db.add_column('viddler_viddlervideo', 'upload_time',
                      self.gf('django.db.models.fields.TimeField')(default=datetime.datetime(2013, 10, 24, 0, 0)),
                      keep_default=False)


    models = {
        'viddler.viddlervideo': {
            'Meta': {'object_name': 'ViddlerVideo'},
            'age_limit': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'audio_only': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'author': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'comment_count': ('django.db.models.fields.IntegerField', [], {}),
            'commenting_permission': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'display_aspect_ratio': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'download_permission': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'embed_code': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'embed_permission': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'favorite': ('django.db.models.fields.IntegerField', [], {}),
            'files': ('django.db.models.fields.TextField', [], {}),
            'html5_video_source': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'impression_count': ('django.db.models.fields.IntegerField', [], {}),
            'key_image_custom': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'key_image_custom_height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'key_image_custom_width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'last_synced': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'length': ('durationfield.db.models.fields.duration.DurationField', [], {}),
            'made_public_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'permalink': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'tagging_permission': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'tags': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'thumb_height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'thumb_width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'thumbnail': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'thumbnail_index': ('django.db.models.fields.IntegerField', [], {}),
            'thumbnail_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'thumbnails_count': ('django.db.models.fields.IntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'upload_time': ('django.db.models.fields.DateTimeField', [], {}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'viddler_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'view_count': ('django.db.models.fields.IntegerField', [], {}),
            'view_permission': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['viddler']