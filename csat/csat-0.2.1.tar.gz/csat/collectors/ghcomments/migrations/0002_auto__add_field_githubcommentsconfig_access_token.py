# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'GithubCommentsConfig.access_token'
        db.add_column(u'ghcomments_githubcommentsconfig', 'access_token',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'GithubCommentsConfig.access_token'
        db.delete_column(u'ghcomments_githubcommentsconfig', 'access_token')


    models = {
        u'acquisition.acquisitionsessionconfig': {
            'Meta': {'ordering': "['created']", 'object_name': 'AcquisitionSessionConfig'},
            'completed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'graph': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'started': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'temporary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'thumbnail': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        u'acquisition.datacollectorconfig': {
            'Meta': {'object_name': 'DataCollectorConfig'},
            'completed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'configurator': ('django.db.models.fields.CharField', [], {'max_length': '44'}),
            'graph': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'output': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_acquisition.datacollectorconfig_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'result_id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'running_instance_id': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'session_config': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'collectors'", 'to': u"orm['acquisition.AcquisitionSessionConfig']"}),
            'started': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'ghcomments.githubcommentsconfig': {
            'Meta': {'object_name': 'GithubCommentsConfig', '_ormbases': [u'acquisition.DataCollectorConfig']},
            'access_token': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            u'datacollectorconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['acquisition.DataCollectorConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'issue_nodes': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'issues_state': ('django.db.models.fields.CharField', [], {'default': "'all'", 'max_length': '63'}),
            'repo_name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['ghcomments']