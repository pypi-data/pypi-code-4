# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):
    depends_on = (
        ("wheelcms_axle", "0001_initial.py"),
    )

    def forwards(self, orm):
        # Adding model 'Configuration'
        db.create_table('wheelcms_disqus_configuration', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('main', self.gf('django.db.models.fields.related.ForeignKey')(related_name='disqus', to=orm['wheelcms_axle.Configuration'])),
            ('shortname', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('wheelcms_disqus', ['Configuration'])


    def backwards(self, orm):
        # Deleting model 'Configuration'
        db.delete_table('wheelcms_disqus_configuration')


    models = {
        'wheelcms_axle.configuration': {
            'Meta': {'object_name': 'Configuration'},
            'analytics': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'head': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mailto': ('django.db.models.fields.EmailField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'sender': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'sendermail': ('django.db.models.fields.EmailField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'theme': ('django.db.models.fields.CharField', [], {'default': "'default'", 'max_length': '256', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256', 'blank': 'True'})
        },
        'wheelcms_disqus.configuration': {
            'Meta': {'object_name': 'Configuration'},
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'main': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'disqus'", 'to': "orm['wheelcms_axle.Configuration']"}),
            'shortname': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        }
    }

    complete_apps = ['wheelcms_disqus']
