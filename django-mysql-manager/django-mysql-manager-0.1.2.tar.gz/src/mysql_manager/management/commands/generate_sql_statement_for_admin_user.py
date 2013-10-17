# -*- coding: utf-8 -*-
#
#  This file is part of django-primary-blog.
#
#  django-primary-blog is a blogging system based on the Django framework.
#
#  Development Web Site:
#    - http://www.codetrax.org/projects/django-primary-blog
#  Public Source Code Repository:
#    - https://source.codetrax.org/hgroot/django-primary-blog
#
#  Copyright 2010 George Notaras <gnot [at] g-loaded.eu>
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

#from optparse import make_option
from django.core.management.base import BaseCommand

from mysql_manager import settings


class Command(BaseCommand):
    
    help = 'Generate an SQL statement that creates the Administrator MySQL user.'
    #args = '[appname ...]'
    requires_model_validation = False
    
    def handle(self, *test_labels, **options):
        privileges = settings.MYMANAGER_DEFAULT_DB_PRIVILEGES
        privileges.extend(['CREATE USER', 'RELOAD'])
        print "CREATE USER 'administrator'@'localhost' IDENTIFIED BY '1234';"
        print "GRANT %s ON *.* TO 'administrator'@'localhost' WITH GRANT OPTION;" % ','.join(privileges)
        

