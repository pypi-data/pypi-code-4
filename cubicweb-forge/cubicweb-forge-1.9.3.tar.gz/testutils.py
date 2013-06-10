"""some utilities for testing forge security

:organization: Logilab
:copyright: 2008-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubes.tracker.testutils import SecurityTC
from cubicweb.devtools import fill
from cubicweb import Binary

class MyValueGenerator(fill.ValueGenerator):
    def generate_Project_icon(self, entity, index, **kw):
        # a valid 1x1 black RGB PNG image
        return Binary('\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00'
                      '\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00'
                      '\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xf6\x178U\x00'
                      '\x00\x00\x00IEND\xaeB`\x82')
    def generate_Project_icon_format(self, entity, index, **kw):
        return 'image/png'

class ForgeSecurityTC(SecurityTC):

    def setUp(self):
        SecurityTC.setUp(self)
        # implicitly test manager can add some entities
        req = self.request()
        req.create_entity('License', name=u'license')
        self.extproject = req.create_entity('ExtProject', name=u'projet externe')
        self.commit()
