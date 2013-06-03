# -*- coding: utf-8 -*-

################################################################
# vs.org (C) 2011, Veit Schiele
################################################################

# $Id$

import urllib

from plone.memoize.instance import memoize
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from zope.interface import implements

from .interfaces import IVBBView

class VBBView(BrowserView):
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
                                
    @memoize
    def getVBBUrl(self):
        """ VBB Link """
        ret=u''
        country = self.context.getCountry()
#        if country not in ['de']:
#            return u''

        vbb = 'http://www.vbb-fahrinfo.de/fahrinfo/bin/query.exe/dn'
        data={}
        data['L'] ='impuls'
        to=u''

        addresses = self.context.getAddresses()
        address = None
        if len(addresses):
            address = addresses[0]

        if not address or address.get('poBox') != '':
             return

        zip = address.get('zipCode')
        city = address.get('city').decode('utf-8')
        street = address.get('street').decode('utf-8')

        if zip:
            to += """%s """ %(zip)
        if city:
            to += """%s """ %(city)
        if street:
            street=street.replace(u'Straße','Str.')
            street=street.replace(u'Strasse','Str.')
            to += street

        data['to'] = to.encode('ISO-8859-1')
        data['toType'] ='ADDRESS'
        data['REQ0HafasSearchForw'] = '0'
        data['REQ0JourneyStopsS0B'] = '5'
        data['REQ0JourneyStopsZ0B'] = '5'
        data['iER']='yes'
        if vbb:
            ret = vbb + u'?' + urllib.urlencode(data)
        return ret
    
    
