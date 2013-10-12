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
        # Adding unique constraint on 'Entity', fields ['project', 'name']
        db.create_unique(u'conntrackt_entity', ['project_id', 'name'])

        # Adding unique constraint on 'Location', fields ['name']
        db.create_unique(u'conntrackt_location', ['name'])

        # Adding unique constraint on 'Interface', fields ['name', 'entity']
        db.create_unique(u'conntrackt_interface', ['name', 'entity_id'])

        # Adding unique constraint on 'Project', fields ['name']
        db.create_unique(u'conntrackt_project', ['name'])


    def backwards(self, orm):
        # Removing unique constraint on 'Project', fields ['name']
        db.delete_unique(u'conntrackt_project', ['name'])

        # Removing unique constraint on 'Interface', fields ['name', 'entity']
        db.delete_unique(u'conntrackt_interface', ['name', 'entity_id'])

        # Removing unique constraint on 'Location', fields ['name']
        db.delete_unique(u'conntrackt_location', ['name'])

        # Removing unique constraint on 'Entity', fields ['project', 'name']
        db.delete_unique(u'conntrackt_entity', ['project_id', 'name'])


    models = {
        u'conntrackt.communication': {
            'Meta': {'unique_together': "(('source', 'destination', 'protocol', 'port'),)", 'object_name': 'Communication'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'destination': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'destination_set'", 'to': u"orm['conntrackt.Interface']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'port': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'protocol': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'source_set'", 'to': u"orm['conntrackt.Interface']"})
        },
        u'conntrackt.entity': {
            'Meta': {'unique_together': "(('name', 'project'),)", 'object_name': 'Entity'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['conntrackt.Location']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['conntrackt.Project']"})
        },
        u'conntrackt.interface': {
            'Meta': {'unique_together': "(('name', 'entity'),)", 'object_name': 'Interface'},
            'address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "'Main network interface.'", 'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['conntrackt.Entity']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'eth0'", 'max_length': '100'}),
            'netmask': ('django.db.models.fields.IPAddressField', [], {'default': "'255.255.255.255'", 'max_length': '15'})
        },
        u'conntrackt.location': {
            'Meta': {'object_name': 'Location'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'conntrackt.project': {
            'Meta': {'object_name': 'Project'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        }
    }

    complete_apps = ['conntrackt']