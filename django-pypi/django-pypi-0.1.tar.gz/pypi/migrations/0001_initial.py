# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Package'
        db.create_table(u'pypi_package', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
        ))
        db.send_create_signal(u'pypi', ['Package'])

        # Adding model 'Version'
        db.create_table(u'pypi_version', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('package', self.gf('django.db.models.fields.related.ForeignKey')(related_name='versions', to=orm['pypi.Package'])),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal(u'pypi', ['Version'])

        # Adding unique constraint on 'Version', fields ['package', 'version']
        db.create_unique(u'pypi_version', ['package_id', 'version'])

        # Adding model 'Release'
        db.create_table(u'pypi_release', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('version', self.gf('django.db.models.fields.related.ForeignKey')(related_name='releases', to=orm['pypi.Version'])),
            ('has_sig', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('md5_digest', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('comment_text', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('python_version', self.gf('django.db.models.fields.CharField')(max_length=6)),
            ('upload_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('packagetype', self.gf('django.db.models.fields.CharField')(max_length=9)),
            ('downloads', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('size', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'pypi', ['Release'])

        # Adding unique constraint on 'Release', fields ['version', 'upload_time']
        db.create_unique(u'pypi_release', ['version_id', 'upload_time'])


    def backwards(self, orm):
        # Removing unique constraint on 'Release', fields ['version', 'upload_time']
        db.delete_unique(u'pypi_release', ['version_id', 'upload_time'])

        # Removing unique constraint on 'Version', fields ['package', 'version']
        db.delete_unique(u'pypi_version', ['package_id', 'version'])

        # Deleting model 'Package'
        db.delete_table(u'pypi_package')

        # Deleting model 'Version'
        db.delete_table(u'pypi_version')

        # Deleting model 'Release'
        db.delete_table(u'pypi_release')


    models = {
        u'pypi.package': {
            'Meta': {'object_name': 'Package'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'pypi.release': {
            'Meta': {'ordering': "('version', 'upload_time')", 'unique_together': "(('version', 'upload_time'),)", 'object_name': 'Release'},
            'comment_text': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'downloads': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'has_sig': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'md5_digest': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'packagetype': ('django.db.models.fields.CharField', [], {'max_length': '9'}),
            'python_version': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'size': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'upload_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'releases'", 'to': u"orm['pypi.Version']"})
        },
        u'pypi.version': {
            'Meta': {'unique_together': "(('package', 'version'),)", 'object_name': 'Version'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'versions'", 'to': u"orm['pypi.Package']"}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['pypi']