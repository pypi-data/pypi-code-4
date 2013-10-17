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

from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _

from mysql_manager import signal_cb
from mysql_manager import managers



class MySQLUser(models.Model):
    
    name = models.SlugField(max_length=55, db_index=True, unique=True, verbose_name=_('name'), help_text='''Enter a name for the MySQL user''')
    is_active = models.BooleanField(default=True, db_index=True, verbose_name='active', help_text='''Mark the user as active or not. A user that is marked as inactive cannot login to the PostgreSQL cluster.''')
    
    max_queries_per_hour = models.PositiveIntegerField(default=0, verbose_name='max queries per hour', help_text="""Restrict the number of queries permitted to this account during any given one-hour period. If this is set to 0 (the default), this means that there is no limitation for the account.""")
    max_updates_per_hour = models.PositiveIntegerField(default=0, verbose_name='max updates per hour', help_text="""Restrict the number of updates permitted to this account during any given one-hour period. If this is set to 0 (the default), this means that there is no limitation for the account.""")
    max_connections_per_hour = models.PositiveIntegerField(default=0, verbose_name='max connections per hour', help_text="""Restrict the number of connections permitted to this account during any given one-hour period. If this is set to 0 (the default), this means that there is no limitation for the account.""")
    max_user_connections= models.PositiveIntegerField(default=0, verbose_name='max user connections', help_text="""Restricts the maximum number of simultaneous connections to the server by the account. A nonzero value specifies the limit for the account explicitly. If value is 0 (the default), the server determines the number of simultaneous connections for the account from the global value of the ``max_user_connections`` system variable. If ``max_user_connections`` is also zero, there is no limit for the account.""")
    
    date_created = models.DateTimeField(verbose_name='created on', auto_now_add=True)
    date_modified = models.DateTimeField(verbose_name='last modified on', auto_now=True)
    created_by = models.ForeignKey('auth.User', related_name='%(app_label)s_%(class)s_created_by')
    
    objects = managers.MySQLUserManager()
    
    class Meta:
        verbose_name = 'MySQL User'
        verbose_name_plural = 'MySQL Users'
        ordering = ('name',)
    
    def __unicode__(self):
        return self.name

signals.pre_delete.connect(signal_cb.drop_user, sender=MySQLUser)



class MySQLDatabase(models.Model):
    
    name = models.SlugField(max_length=100, db_index=True, unique=True, verbose_name='name', help_text='''Enter a name for the PostgreSQL database.''')
    user = models.ForeignKey('mysql_manager.MySQLUser', related_name='%(app_label)s_%(class)s_user', on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_('user'), help_text='''Select the user that owns the database.''')
    charset_name = models.CharField(max_length=30, default='utf8', verbose_name='character set', help_text='''Enter the character set for this database.''')
    collation_name = models.CharField(max_length=30, default='utf8_unicode_ci', verbose_name='collation', help_text='''Enter the collation for this database.''')
    
    date_created = models.DateTimeField(verbose_name='created on', auto_now_add=True)
    date_modified = models.DateTimeField(verbose_name='last modified on', auto_now=True)
    created_by = models.ForeignKey('auth.User', related_name='%(app_label)s_%(class)s_created_by')
    
    objects = managers.MySQLDatabaseManager()
    
    class Meta:
        verbose_name = 'MySQL Database'
        verbose_name_plural = 'MySQL Databases'
        ordering = ('name',)

    def __unicode__(self):
        return self.name

signals.pre_delete.connect(signal_cb.drop_database, sender=MySQLDatabase)


