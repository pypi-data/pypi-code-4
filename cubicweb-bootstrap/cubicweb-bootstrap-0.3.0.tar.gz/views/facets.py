"""bootstrap implementation of facets

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from cubicweb.web.views import facets

facets.FilterBox.bk_linkbox_template = u'<p class="btn btn-default btn-sm btn-facet">%s</p>'
