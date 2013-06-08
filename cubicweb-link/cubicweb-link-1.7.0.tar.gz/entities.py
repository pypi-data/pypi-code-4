"""entity classes for Link entities

:organization: Logilab
:copyright: 2003-2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.entities import AnyEntity, fetch_config

class Link(AnyEntity):
    """customized class for Link entities"""
    __regid__ = 'Link'
    fetch_attrs, fetch_order = fetch_config(['title', 'url'])

    def dc_title(self):
        return u'%s (%s)' % (self.title, self.url)

