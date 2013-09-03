# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'ViddlerVideo.embed_code'
        db.add_column('viddler_viddlervideo', 'embed_code',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'ViddlerVideo.key_image_custom'
        db.add_column('viddler_viddlervideo', 'key_image_custom',
                      self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding field 'ViddlerVideo.key_image_custom_width'
        db.add_column('viddler_viddlervideo', 'key_image_custom_width',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'ViddlerVideo.key_image_custom_height'
        db.add_column('viddler_viddlervideo', 'key_image_custom_height',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

    def backwards(self, orm):
        # Deleting field 'ViddlerVideo.embed_code'
        db.delete_column('viddler_viddlervideo', 'embed_code')

        # Deleting field 'ViddlerVideo.key_image_custom'
        db.delete_column('viddler_viddlervideo', 'key_image_custom')

        # Deleting field 'ViddlerVideo.key_image_custom_width'
        db.delete_column('viddler_viddlervideo', 'key_image_custom_width')

        # Deleting field 'ViddlerVideo.key_image_custom_height'
        db.delete_column('viddler_viddlervideo', 'key_image_custom_height')

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
            'embed_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
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
            'made_public_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'permalink': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'tagging_permission': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'tags': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'thumbnail_index': ('django.db.models.fields.IntegerField', [], {}),
            'thumbnail_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'thumbnails_count': ('django.db.models.fields.IntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'upload_time': ('django.db.models.fields.TimeField', [], {}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'viddler_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'view_count': ('django.db.models.fields.IntegerField', [], {}),
            'view_permission': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['viddler']
