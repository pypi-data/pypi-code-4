# -*- coding: utf-8 -*-

import datetime
import codecs
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import django.contrib.auth.models
import sys, csv, os.path, re, datetime
import django.template.defaultfilters
import settings

class Command(BaseCommand):
    args = ''

    help = u"Exports the DB config in BASH syntax"

    def handle(self, *args, **options):
        for dbname, db in settings.DATABASES.iteritems():
            for key, value in db.iteritems():
                print 'export DB_%s_%s="%s"' % (dbname.upper(), key.upper(), value)
