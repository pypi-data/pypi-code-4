#!/usr/bin/env python
# Copyright (C) 2010 Etienne Robillard <erob@gthcfoundation.org>
# All rights reserved
#
# <LICENSE>

import sys, os
import argparse
import datetime
import schevo.database as Database
import schevo.constant as constant
import schevo.entity   as entity
import schevo.fieldspec as fieldspec
import demjson
#import unicodedata

from notmm.utils.django_settings import SettingsProxy
settings = SettingsProxy('moviereviews_generic.settings', autoload=True).get_settings()

from test_support import unittest, inittestpackage
inittestpackage()

from model import ActorManager, db
db = Database.open(settings.DATABASE_NAME)
UNASSIGNED = constant.UNASSIGNED
escape_unicode = False

def extent_to_dict(instance, f="_field_spec"):
    """
    Convert a ``schevo.extent.Extent`` instance attributes to a flattened ``dict``
    object.

    """
    rv = {}
    for name, field in getattr(instance, f).items():
        #XXX: save the field type here? 
        obj = getattr(instance, name)
        if obj is UNASSIGNED: 
            # convert UNASSIGNED fields to None
            fdata = None
        elif isinstance(obj, (datetime.datetime, datetime.date)):
            # convert datetime objects to a string type
            fdata = obj.strftime("%Y-%M-%d@%H:%S") # format?
        else:
            # follow foreing relationships
            if hasattr(obj, 's'):
                #field_spec = getattr(obj, f)
                fdata = obj.s.field_map()
                for k,v in fdata.items():
                    #fdata[k] = "%s"%unicodedata.normalize('NFC', unicode(v))
                    if not v is UNASSIGNED:
                        fdata[k] = str(v)
            else:
                fdata = obj
        rv[name] = fdata        
    return rv   

#TODO: relocate this as a bound method to RelationProxy (==0.4.3)
def dump_all(db):
    result = []
    info_map = {}
    for x in [ext for ext in db.extents()]:
        info_map[x.name] = [extent_to_dict(item) for item in x.find()]
        result.append(info_map)
    return result

class FieldSpecTestCase(unittest.TestCase):

    def setUp(self):
        # New-style django settings loading
        pass

    def runTest(self):
        pass

    def test_dump_all(self):

        # Verify the database name

        info_map = dump_all(db)
        self.failUnlessEqual(isinstance(info_map, list), True)
        
        # save the info_map to a file in json format
        # json = demjson.encode(info_map, strict=True)
        #f = 'test.json'
        #open(f, 'w').write(json.decode())
        #os.unlink('test.json')

