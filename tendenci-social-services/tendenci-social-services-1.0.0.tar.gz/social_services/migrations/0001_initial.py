# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'SkillSet'
        db.create_table('social_services_skillset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('paramedic', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('fireman', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('first_aid', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('safety_manager', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('police', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('search_and_rescue', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('scuba_certified', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('crowd_control', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('truck', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('pilot', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('aircraft', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('ship', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('sailor', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('doctor', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('nurse', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('medical_specialty', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('crisis_communication', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('media', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('author', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('public_speaker', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('politician', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('blogger', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('photographer', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('videographer', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('radio_operator', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('call_sign', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('actor', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('thought_leader', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('influencer', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('languages', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('teacher', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('school_admin', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('military_rank', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('military_training', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('desert_trained', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('cold_trained', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('marksman', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('security_clearance', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('loc', self.gf('django.contrib.gis.db.models.fields.PointField')(null=True, blank=True)),
        ))
        db.send_create_signal('social_services', ['SkillSet'])

        # Adding model 'ReliefAssessment'
        db.create_table('social_services_reliefassessment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('id_number', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('issuing_authority', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('health_insurance', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('insurance_provider', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('address2', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('zipcode', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('alt_address', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('alt_address2', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('alt_city', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('alt_state', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('alt_zipcode', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('alt_country', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('ethnicity', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('other_ethnicity', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('below_2', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('between_3_11', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('between_12_18', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('between_19_59', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('above_60', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('ssa', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('dhs', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('children_needs', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('toiletries', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('employment', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('training', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('food', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('gas', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('prescription', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('other_service', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('case_notes', self.gf('tinymce.models.HTMLField')(null=True, blank=True)),
            ('items_provided', self.gf('tinymce.models.HTMLField')(null=True, blank=True)),
            ('loc', self.gf('django.contrib.gis.db.models.fields.PointField')(null=True, blank=True)),
        ))
        db.send_create_signal('social_services', ['ReliefAssessment'])


    def backwards(self, orm):
        
        # Deleting model 'SkillSet'
        db.delete_table('social_services_skillset')

        # Deleting model 'ReliefAssessment'
        db.delete_table('social_services_reliefassessment')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 6, 1, 18, 2, 24, 623358)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 6, 1, 18, 2, 24, 623240)'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'social_services.reliefassessment': {
            'Meta': {'object_name': 'ReliefAssessment'},
            'above_60': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'address': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'address2': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'alt_address': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'alt_address2': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'alt_city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'alt_country': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'alt_state': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'alt_zipcode': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'below_2': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'between_12_18': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'between_19_59': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'between_3_11': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'case_notes': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'children_needs': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'dhs': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'employment': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ethnicity': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'food': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'gas': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'health_insurance': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_number': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'insurance_provider': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'issuing_authority': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'items_provided': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'loc': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'}),
            'other_ethnicity': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'other_service': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'prescription': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ssa': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'toiletries': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'training': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'social_services.skillset': {
            'Meta': {'object_name': 'SkillSet'},
            'actor': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'aircraft': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'author': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'blogger': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'call_sign': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'cold_trained': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'crisis_communication': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'crowd_control': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'desert_trained': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'doctor': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'fireman': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'first_aid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'influencer': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'languages': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'loc': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'}),
            'marksman': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'media': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'medical_specialty': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'military_rank': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'military_training': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'nurse': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'paramedic': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'photographer': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'pilot': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'police': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'politician': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'public_speaker': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'radio_operator': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'safety_manager': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sailor': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'school_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'scuba_certified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'search_and_rescue': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'security_clearance': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'ship': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'teacher': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'thought_leader': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'truck': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'}),
            'videographer': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['social_services']
