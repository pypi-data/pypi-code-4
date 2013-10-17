# -*- coding: utf-8 -*-
#
#  This file is part of django-mysql-manager.
#
#  django-mysql-manager is a Django based management interface for MySQL users and databases.
#
#  Development Web Site:
#    - http://www.codetrax.org/projects/django-mysql-manager
#  Public Source Code Repository:
#    - https://source.codetrax.org/hgroot/django-mysql-manager
#
#  Copyright 2011 George Notaras <gnot [at] g-loaded.eu>
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

from django.contrib import admin
from django.db.models.loading import cache

from mysql_manager.forms import MySQLUserModelForm, MySQLDatabaseModelForm
from mysql_manager.actions import reset_database


class MySQLUserAdmin(admin.ModelAdmin):

    form = MySQLUserModelForm
    list_display = ('name', 'date_created', 'max_queries_per_hour',
        'max_updates_per_hour', 'max_connections_per_hour', 'max_user_connections')
    search_fields = ('name', )
    
    def get_form(self, request, obj=None, **kwargs):
        if obj is None:     # This is the add form
            self.fields = ['name', 'password1', 'password2',
                'max_queries_per_hour', 'max_updates_per_hour',
                'max_connections_per_hour', 'max_user_connections']
        else:               # This is the change form
            self.fields = ['name', 'password1', 'password2',
                'date_created', 'date_modified',
                'max_queries_per_hour', 'max_updates_per_hour',
                'max_connections_per_hour', 'max_user_connections']
            if request.user.is_superuser:
                self.fields.append('created_by')
        return super(MySQLUserAdmin, self).get_form(request, obj, **kwargs)
    
    def get_readonly_fields(self, request, obj=None):
        if obj is None:     # This is the add form
            self.readonly_fields = []
        else:               # This is the change form
            self.readonly_fields = ['name', 'date_created', 'date_modified']
            if request.user.is_superuser:
                self.readonly_fields.append('created_by')
        return super(MySQLUserAdmin, self).get_readonly_fields(request, obj)
    
    def queryset(self, request):
        qs = super(MySQLUserAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(created_by=request.user)
    
    def save_model(self, request, obj, form, change):
        MySQLUser = cache.get_model('mysql_manager', 'MySQLUser')
        password = form.cleaned_data.get('password1')
        
        if not change:  # User creation form
            
            assert password != '', 'A password is mandatory for new accounts'
            
            # The ``created_by`` attribute is set once at creation time
            obj.created_by = request.user
            
            MySQLUser.objects.create_user(obj.name, password)
            MySQLUser.objects.set_limits(obj.name, obj.max_queries_per_hour,
                obj.max_updates_per_hour, obj.max_connections_per_hour, obj.max_user_connections)
            
        else:   # This is the change form
            
            if 'max_queries_per_hour' in form.changed_data or \
                    'max_updates_per_hour' in form.changed_data or \
                    'max_connections_per_hour' in form.changed_data or \
                    'max_user_connections' in form.changed_data:
                MySQLUser.objects.set_limits(obj.name, obj.max_queries_per_hour,
                    obj.max_updates_per_hour, obj.max_connections_per_hour, obj.max_user_connections)
            
            if password:
                MySQLUser.objects.change_password(obj.name, password)
 
        # Save the model
        obj.save()

admin.site.register(cache.get_model('mysql_manager', 'MySQLUser'), MySQLUserAdmin)



class MySQLDatabaseAdmin(admin.ModelAdmin):

    form = MySQLDatabaseModelForm
    list_display = ('name', 'user', 'charset_name', 'collation_name', 'date_created')
    
    search_fields = ('name', 'owner__name')
    
    actions = [reset_database, ]
    
    def get_form(self, request, obj=None, **kwargs):
        if obj is None:     # This is the add form
            self.fields = ['name', 'user', 'charset_name', 'collation_name']
        else:               # This is the change form
            self.fields = ['name', 'user', 'charset_name', 'collation_name', 'date_created', 'date_modified']
            if request.user.is_superuser:
                self.fields.append('created_by')
        return super(MySQLDatabaseAdmin, self).get_form(request, obj, **kwargs)
    
    def get_readonly_fields(self, request, obj=None):
        if obj is None:     # This is the add form
            self.readonly_fields = []
        else:               # This is the change form
            self.readonly_fields = ['name', 'date_created', 'date_modified']
            if request.user.is_superuser:
                self.readonly_fields.append('created_by')
        return super(MySQLDatabaseAdmin, self).get_readonly_fields(request, obj)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        MySQLUser = cache.get_model('mysql_manager', 'MySQLUser')
        if db_field.name == 'user':
            if not request.user.is_superuser:
                kwargs['queryset'] = MySQLUser.objects.filter(created_by=request.user)
        return super(MySQLDatabaseAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
    
    def queryset(self, request):
        qs = super(MySQLDatabaseAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(created_by=request.user)
    
    def save_model(self, request, obj, form, change):
        MySQLDatabase = cache.get_model('mysql_manager', 'MySQLDatabase')
        
        if not change:  # Database creation form
            
            # The ``created_by`` attribute is set once at creation time
            obj.created_by = request.user
            
            MySQLDatabase.objects.create_database(obj.name, obj.charset_name, obj.collation_name)
            
            if obj.user:
                MySQLDatabase.objects.grant_privileges(obj.name, obj.user.name)
        
        else:   # This is the change form
            
            if 'charset_name' in form.changed_data or 'collation_name' in form.changed_data:
                MySQLDatabase.objects.change_specification(obj.name, obj.charset_name, obj.collation_name)
            
            if 'user' in form.changed_data:
                # First revoke all privileges on the old database.
                old_user_id = form.initial.get('user', None)
                if old_user_id is not None:
                    # old_user_id can be none in cases where it has never been set before.
                    MySQLUser = cache.get_model('mysql_manager', 'MySQLUser')
                    old_user = MySQLUser.objects.get(id__exact=old_user_id)
                    MySQLDatabase.objects.revoke_privileges(obj.name, old_user.name)

            if obj.user:
                # Now grant all privileges to the new owner
                MySQLDatabase.objects.grant_privileges(obj.name, obj.user.name)
                
        # Save the model
        obj.save()

admin.site.register(cache.get_model('mysql_manager', 'MySQLDatabase'), MySQLDatabaseAdmin)

