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
from django.db import connections

from mysql_manager import settings


class BasePgManager(models.Manager):
    
    MYMANAGER_DB_ALIAS = 'mysql_manager_conn'
    
    DEFAULT_DB_PRIVILEGES = ','.join(settings.MYMANAGER_DEFAULT_DB_PRIVILEGES)
    
    def execute_custom_query(self, sql):
        #print sql
        connection = connections[self.MYMANAGER_DB_ALIAS]
        cursor = connection.cursor()
        cursor.execute(sql)


class MySQLUserManager(BasePgManager):
    
    def create_user(self, username, password):
        self.execute_custom_query(
            "CREATE USER '%s'@'localhost' IDENTIFIED BY '%s'" % (username, password))
        self.execute_custom_query("FLUSH PRIVILEGES")
    
    def drop_user(self, username):
        self.execute_custom_query("DROP USER '%s'@'localhost'" % username)
        self.execute_custom_query("FLUSH PRIVILEGES")
    
    def change_password(self, username, password):
        self.execute_custom_query("SET PASSWORD FOR '%s'@'localhost' = PASSWORD('%s')" % (username, password))

    def set_limits(self, username, max_queries_per_hour,
            max_updates_per_hour, max_connections_per_hour, max_user_connections):
        """
        These limits are set on a per user basisand cannot be combined with a
        specific database.
        
        Therefore we use the general ``USAGE ON *.*`` privilege here. Database
        specific privileges are set by the MySQLDatabaseManager.grant_privileges()
        method.
        """
        self.execute_custom_query("GRANT USAGE ON *.* TO '%(username)s'@'localhost' \
            WITH MAX_QUERIES_PER_HOUR %(max_queries_per_hour)s \
            MAX_UPDATES_PER_HOUR %(max_updates_per_hour)s \
            MAX_CONNECTIONS_PER_HOUR %(max_connections_per_hour)s \
            MAX_USER_CONNECTIONS %(max_user_connections)s" % {
                'username': username,
                'max_queries_per_hour': max_queries_per_hour,
                'max_updates_per_hour': max_updates_per_hour,
                'max_connections_per_hour': max_connections_per_hour,
                'max_user_connections': max_user_connections,
            }
        )

class MySQLDatabaseManager(BasePgManager):
    
    def create_database(self, database, charset, collation):
        self.execute_custom_query(
            "CREATE DATABASE %(database)s CHARACTER SET %(charset)s COLLATE %(collation)s" % {
                'database': database, 'charset': charset, 'collation': collation})
    
    def drop_database(self, database):
        self.execute_custom_query("DROP DATABASE %s" % database)
    
    def change_specification(self, database, charset, collation):
        self.execute_custom_query("ALTER DATABASE %s CHARACTER SET %s COLLATE %s" % (database, charset, collation))
    
    def grant_privileges(self, database, username):
        self.execute_custom_query("GRANT %(privileges)s ON `%(database)s`.* TO '%(username)s'@'localhost'" % {
            'privileges': self.DEFAULT_DB_PRIVILEGES,
            'database': database,
            'username': username,
        })
        self.execute_custom_query("FLUSH PRIVILEGES")
    
    def revoke_privileges(self, database, username):
        self.execute_custom_query("REVOKE %s ON `%s`.* FROM '%s'@'localhost'" % (
            self.DEFAULT_DB_PRIVILEGES, database, username))
        self.execute_custom_query("FLUSH PRIVILEGES")

