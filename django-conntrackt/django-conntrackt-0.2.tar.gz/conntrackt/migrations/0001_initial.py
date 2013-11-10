# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Branko Majic
#
# This file is part of Django Conntrackt.
#
# Django Conntrackt is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Django Conntrackt is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# Django Conntrackt.  If not, see <http://www.gnu.org/licenses/>.
#


# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Project'
        db.create_table('conntrackt_project', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('conntrackt', ['Project'])

        # Adding model 'Location'
        db.create_table('conntrackt_location', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('conntrackt', ['Location'])

        # Adding model 'Entity'
        db.create_table('conntrackt_entity', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['conntrackt.Project'])),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['conntrackt.Location'])),
        ))
        db.send_create_signal('conntrackt', ['Entity'])

        # Adding model 'Interface'
        db.create_table('conntrackt_interface', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='eth0', max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(default='Main network interface.', blank=True)),
            ('entity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['conntrackt.Entity'])),
            ('address', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('netmask', self.gf('django.db.models.fields.IPAddressField')(default='255.255.255.255', max_length=15)),
        ))
        db.send_create_signal('conntrackt', ['Interface'])

        # Adding model 'Communication'
        db.create_table('conntrackt_communication', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(related_name='source_set', to=orm['conntrackt.Interface'])),
            ('destination', self.gf('django.db.models.fields.related.ForeignKey')(related_name='destination_set', to=orm['conntrackt.Interface'])),
            ('protocol', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('port', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('conntrackt', ['Communication'])


    def backwards(self, orm):
        # Deleting model 'Project'
        db.delete_table('conntrackt_project')

        # Deleting model 'Location'
        db.delete_table('conntrackt_location')

        # Deleting model 'Entity'
        db.delete_table('conntrackt_entity')

        # Deleting model 'Interface'
        db.delete_table('conntrackt_interface')

        # Deleting model 'Communication'
        db.delete_table('conntrackt_communication')


    models = {
        'conntrackt.communication': {
            'Meta': {'object_name': 'Communication'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'destination': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'destination_set'", 'to': "orm['conntrackt.Interface']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'port': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'protocol': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'source_set'", 'to': "orm['conntrackt.Interface']"})
        },
        'conntrackt.entity': {
            'Meta': {'object_name': 'Entity'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['conntrackt.Location']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['conntrackt.Project']"})
        },
        'conntrackt.interface': {
            'Meta': {'object_name': 'Interface'},
            'address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "'Main network interface.'", 'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['conntrackt.Entity']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'eth0'", 'max_length': '100'}),
            'netmask': ('django.db.models.fields.IPAddressField', [], {'default': "'255.255.255.255'", 'max_length': '15'})
        },
        'conntrackt.location': {
            'Meta': {'object_name': 'Location'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'conntrackt.project': {
            'Meta': {'object_name': 'Project'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['conntrackt']