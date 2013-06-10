"""Specific views for address book entities (eg PhoneNumber and PostalAddress)

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from logilab.mtconverter import xml_escape

from cubicweb.view import EntityView
from cubicweb.selectors import is_instance
from cubicweb.web import uicfg
from cubicweb.web.views import baseviews

uicfg.indexview_etype_section['PhoneNumber'] = 'subobject'
uicfg.indexview_etype_section['PostalAddress'] = 'subobject'
uicfg.indexview_etype_section['IMAddress'] = 'subobject'

uicfg.autoform_section.tag_attribute(('PostalAddress', 'latitude'), 'main', 'hidden')
uicfg.autoform_section.tag_attribute(('PostalAddress', 'longitude'), 'main', 'hidden')

class PhoneNumberInContextView(baseviews.InContextView):
    __select__ = is_instance('PhoneNumber')

    def cell_call(self, row, col=0):
        self.w(xml_escape(self.cw_rset.get_entity(row, col).dc_title()))

class PhoneNumberListItemView(baseviews.ListItemView):
    __select__ = is_instance('PhoneNumber')

    def cell_call(self, row, col=0, vid=None):
        entity = self.cw_rset.get_entity(row, col)
        self.w(u'<div class="tel"><span class="type">%s</span> %s</div>'
               % (xml_escape(entity.type),
                  xml_escape(entity.number)))

class PhoneNumberSipView(EntityView):
    __regid__ = u'sip'
    __select__ = is_instance('PhoneNumber')

    def cell_call(self, row, col, contexteid=None):
        entity = self.cw_rset.get_entity(row, col)
        self.w(u'<div class="phonenumber">')
        number = xml_escape(entity.number)
        self.w(u'<a href="sip:%s">%s</a>' % (number.replace(" ", ""), number))
        self.w(u'</div>')


class PostalAddressInContextView(baseviews.InContextView):
    __select__ = is_instance('PostalAddress')

    def cell_call(self, row, col, contexteid=None):
        entity = self.cw_rset.get_entity(row, col)
        self.w(u'<div class="adr">')
        if entity.street: # may be set optional by client cubes
            self.w(u'<div class="street-address">%s' %
                   xml_escape(entity.street))
            if entity.street2:
                self.w(u'<br/>')
                self.w(xml_escape(entity.street2)) # FIXME div-class
            self.w(u'</div>')
        if entity.postalcode:
            self.w(u'<span class="postal-code">%s</span> - '
                   % xml_escape(entity.postalcode))
        if entity.city:
            self.w(u'<span class="locality">%s</span>'
                   % xml_escape(entity.city))
        if entity.state:
            self.w(u'<br/>')
            self.w(u'<span class="region">%s</span>' % xml_escape(entity.state))
        if entity.country:
            self.w(u'<br/>')
            self.w(u'<span class="country-name">%s</span>'
                   % xml_escape(entity.country))
        self.w(u'</div>\n')
