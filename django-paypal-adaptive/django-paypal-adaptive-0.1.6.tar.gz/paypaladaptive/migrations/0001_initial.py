# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Payment'
        db.create_table('paypaladaptive_payment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('money_currency', self.gf('money.contrib.django.models.fields.CurrencyField')(default=None, max_length=3)),
            ('money', self.gf('money.contrib.django.models.fields.MoneyField')(default=None, no_currency_field=True, max_digits=6, decimal_places=2, blank=True)),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('secret_uuid', self.gf('paypaladaptive.models.UUIDField')(max_length=32)),
            ('debug_request', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('debug_response', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('pay_key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('transaction_id', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='new', max_length=10)),
            ('status_detail', self.gf('django.db.models.fields.CharField')(max_length=2048)),
        ))
        db.send_create_signal('paypaladaptive', ['Payment'])

        # Adding model 'Refund'
        db.create_table('paypaladaptive_refund', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('money_currency', self.gf('money.contrib.django.models.fields.CurrencyField')(default=None, max_length=3)),
            ('money', self.gf('money.contrib.django.models.fields.MoneyField')(default=None, no_currency_field=True, max_digits=6, decimal_places=2, blank=True)),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('secret_uuid', self.gf('paypaladaptive.models.UUIDField')(max_length=32)),
            ('debug_request', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('debug_response', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('payment', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['paypaladaptive.Payment'], unique=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='new', max_length=10)),
            ('status_detail', self.gf('django.db.models.fields.CharField')(max_length=2048)),
        ))
        db.send_create_signal('paypaladaptive', ['Refund'])

        # Adding model 'Preapproval'
        db.create_table('paypaladaptive_preapproval', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('money_currency', self.gf('money.contrib.django.models.fields.CurrencyField')(default=None, max_length=3)),
            ('money', self.gf('money.contrib.django.models.fields.MoneyField')(default=None, no_currency_field=True, max_digits=6, decimal_places=2, blank=True)),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('secret_uuid', self.gf('paypaladaptive.models.UUIDField')(max_length=32)),
            ('debug_request', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('debug_response', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('valid_until_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 9, 2, 0, 0))),
            ('preapproval_key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('status', self.gf('django.db.models.fields.CharField')(default='new', max_length=10)),
            ('status_detail', self.gf('django.db.models.fields.CharField')(max_length=2048)),
        ))
        db.send_create_signal('paypaladaptive', ['Preapproval'])


    def backwards(self, orm):
        # Deleting model 'Payment'
        db.delete_table('paypaladaptive_payment')

        # Deleting model 'Refund'
        db.delete_table('paypaladaptive_refund')

        # Deleting model 'Preapproval'
        db.delete_table('paypaladaptive_preapproval')


    models = {
        'paypaladaptive.payment': {
            'Meta': {'object_name': 'Payment'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'debug_request': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'debug_response': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'money': ('money.contrib.django.models.fields.MoneyField', [], {'default': 'None', 'no_currency_field': 'True', 'max_digits': '6', 'decimal_places': '2', 'blank': 'True'}),
            'money_currency': ('money.contrib.django.models.fields.CurrencyField', [], {'default': 'None', 'max_length': '3'}),
            'pay_key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'secret_uuid': ('paypaladaptive.models.UUIDField', [], {'max_length': '32'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'new'", 'max_length': '10'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'transaction_id': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'})
        },
        'paypaladaptive.preapproval': {
            'Meta': {'object_name': 'Preapproval'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'debug_request': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'debug_response': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'money': ('money.contrib.django.models.fields.MoneyField', [], {'default': 'None', 'no_currency_field': 'True', 'max_digits': '6', 'decimal_places': '2', 'blank': 'True'}),
            'money_currency': ('money.contrib.django.models.fields.CurrencyField', [], {'default': 'None', 'max_length': '3'}),
            'preapproval_key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'secret_uuid': ('paypaladaptive.models.UUIDField', [], {'max_length': '32'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'new'", 'max_length': '10'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'valid_until_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 9, 2, 0, 0)'})
        },
        'paypaladaptive.refund': {
            'Meta': {'object_name': 'Refund'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'debug_request': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'debug_response': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'money': ('money.contrib.django.models.fields.MoneyField', [], {'default': 'None', 'no_currency_field': 'True', 'max_digits': '6', 'decimal_places': '2', 'blank': 'True'}),
            'money_currency': ('money.contrib.django.models.fields.CurrencyField', [], {'default': 'None', 'max_length': '3'}),
            'payment': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['paypaladaptive.Payment']", 'unique': 'True'}),
            'secret_uuid': ('paypaladaptive.models.UUIDField', [], {'max_length': '32'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'new'", 'max_length': '10'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'max_length': '2048'})
        }
    }

    complete_apps = ['paypaladaptive']