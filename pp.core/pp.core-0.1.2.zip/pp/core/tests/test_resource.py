# -*- coding=utf-8 *-*

################################################################
# pp.core - Produce & Publish
# (C) 2013, ZOPYX Limited, www.zopyx.com
################################################################

import os
import shutil
import unittest
import tempfile
from pp.core.resource import Resource
from fs.osfs import OSFS

class ResourceTests(unittest.TestCase):

    def setUp(self):
        example_resource = os.path.join(os.path.dirname(__file__), 'example_resource')
        self.fslayer = OSFS(example_resource)

    def testResource(self):
        resource = Resource(self.fslayer)
        assert len(resource.list_resources()) == 2
        assert len(resource.list_resources('.css')) == 1
        assert len(resource.list_resources('.pt')) == 1
        assert len(resource.list_resources('.doom')) == 0
