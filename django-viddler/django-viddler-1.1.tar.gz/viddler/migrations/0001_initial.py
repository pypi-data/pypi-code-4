# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ViddlerVideo'
        db.create_table('viddler_viddlervideo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('viddler_id', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('last_synced', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255)),
            ('length', self.gf('durationfield.db.models.fields.duration.DurationField')()),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('age_limit', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('thumbnail_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('permalink', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('html5_video_source', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('audio_only', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('view_count', self.gf('django.db.models.fields.IntegerField')()),
            ('impression_count', self.gf('django.db.models.fields.IntegerField')()),
            ('upload_time', self.gf('django.db.models.fields.TimeField')()),
            ('made_public_time', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('favorite', self.gf('django.db.models.fields.IntegerField')()),
            ('comment_count', self.gf('django.db.models.fields.IntegerField')()),
            ('tags', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('thumbnails_count', self.gf('django.db.models.fields.IntegerField')()),
            ('thumbnail_index', self.gf('django.db.models.fields.IntegerField')()),
            ('view_permission', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('embed_permission', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('tagging_permission', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('commenting_permission', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('download_permission', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('display_aspect_ratio', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('files', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('viddler', ['ViddlerVideo'])

    def backwards(self, orm):
        # Deleting model 'ViddlerVideo'
        db.delete_table('viddler_viddlervideo')

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
            'embed_permission': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'favorite': ('django.db.models.fields.IntegerField', [], {}),
            'files': ('django.db.models.fields.TextField', [], {}),
            'html5_video_source': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'impression_count': ('django.db.models.fields.IntegerField', [], {}),
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
