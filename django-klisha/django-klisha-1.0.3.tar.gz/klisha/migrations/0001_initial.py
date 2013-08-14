# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Category'
        db.create_table(u'klisha_category', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'klisha', ['Category'])

        # Adding model 'Tag'
        db.create_table(u'klisha_tag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'klisha', ['Tag'])

        # Adding model 'Picture'
        db.create_table(u'klisha_picture', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('published_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('picture', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('views_counter', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['klisha.Category'])),
        ))
        db.send_create_signal(u'klisha', ['Picture'])

        # Adding M2M table for field tags on 'Picture'
        db.create_table(u'klisha_picture_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('picture', models.ForeignKey(orm[u'klisha.picture'], null=False)),
            ('tag', models.ForeignKey(orm[u'klisha.tag'], null=False))
        ))
        db.create_unique(u'klisha_picture_tags', ['picture_id', 'tag_id'])


    def backwards(self, orm):
        # Deleting model 'Category'
        db.delete_table(u'klisha_category')

        # Deleting model 'Tag'
        db.delete_table(u'klisha_tag')

        # Deleting model 'Picture'
        db.delete_table(u'klisha_picture')

        # Removing M2M table for field tags on 'Picture'
        db.delete_table('klisha_picture_tags')


    models = {
        u'klisha.category': {
            'Meta': {'ordering': "['title']", 'object_name': 'Category'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'klisha.picture': {
            'Meta': {'ordering': "['-published_at']", 'object_name': 'Picture'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['klisha.Category']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'picture': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'published_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['klisha.Tag']", 'symmetrical': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'views_counter': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'})
        },
        u'klisha.tag': {
            'Meta': {'ordering': "['title']", 'object_name': 'Tag'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['klisha']