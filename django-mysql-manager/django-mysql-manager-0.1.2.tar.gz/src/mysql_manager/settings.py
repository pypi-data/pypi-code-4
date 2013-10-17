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

from django.conf import settings


_MYMANAGER_FORBIDDEN_USER_NAMES = (
    'mysql',
    'admin',
    'administrator',
    'root',
    'sys',
    'system',
    )
MYMANAGER_FORBIDDEN_USER_NAMES = getattr(settings, 'MYMANAGER_FORBIDDEN_USER_NAMES', _MYMANAGER_FORBIDDEN_USER_NAMES)

_MYMANAGER_FORBIDDEN_DATABASE_NAMES = (
    'mysql',
    'test',
    )
MYMANAGER_FORBIDDEN_DATABASE_NAMES = getattr(settings, 'MYMANAGER_FORBIDDEN_DATABASE_NAMES', _MYMANAGER_FORBIDDEN_DATABASE_NAMES)

_MYMANAGER_DEFAULT_DB_PRIVILEGES = [
        'CREATE',
        'DROP',
        'REFERENCES',
        'ALTER',
        'DELETE',
        'INDEX',
        'INSERT',
        'SELECT',
        'UPDATE',
        'CREATE TEMPORARY TABLES',
        'LOCK TABLES',
        'CREATE VIEW',
        'SHOW VIEW',
        'ALTER ROUTINE',
        'CREATE ROUTINE',
        'EXECUTE',
    #    'FILE',
    ]
MYMANAGER_DEFAULT_DB_PRIVILEGES = getattr(settings, 'MYMANAGER_DEFAULT_DB_PRIVILEGES', _MYMANAGER_DEFAULT_DB_PRIVILEGES)

