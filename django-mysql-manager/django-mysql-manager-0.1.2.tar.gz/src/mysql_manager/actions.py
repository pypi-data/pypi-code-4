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

from django.db.models.loading import cache
from django.contrib import messages


def reset_database(modeladmin, request, queryset):
    MySQLDatabase = cache.get_model('mysql_manager', 'MySQLDatabase')
    n = queryset.count()
    
    for db_obj in queryset:
        
        # Store the database info in variables
        db_name = db_obj.name
        db_user_obj = db_obj.user
        db_charset_name = db_obj.charset_name
        db_collation_name = db_obj.collation_name
        db_created_by_obj = db_obj.created_by
        
        # Delete the current database
        db_obj.delete()
        
        # Create a new database object with the stored info
        new_db_obj = MySQLDatabase(
            name = db_name,
            user = db_user_obj,
            charset_name = db_charset_name,
            collation_name = db_collation_name,
            created_by = db_created_by_obj
            )
        # First create the MySQL database on the MySQL server
        MySQLDatabase.objects.create_database(db_name, db_charset_name, db_collation_name)
        # Grant privileges on the user
        MySQLDatabase.objects.grant_privileges(db_name, db_user_obj.name)
        # Now save the Django object
        new_db_obj.save()
        
    if n:
        messages.info(request, 'Successful reset of %d database(s)' % n)
reset_database.short_description = "Reset database [CAUTION: Data Loss]"

