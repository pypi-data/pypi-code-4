################################################################
# vs.org (C) 2011, Veit Schiele
################################################################

# $Id$

import base64
import logging
from cStringIO import StringIO

from zope.i18n import translate
from zope.interface import implements
from zope.component import getMultiAdapter

from DateTime import DateTime
from plone.memoize.instance import memoize
from Products.Five.browser import BrowserView
from Products.ATContentTypes.lib.calendarsupport import foldLine, n2rn, vformat, rfc2445dt

from .. import config
from ..interfaces import IVCardData
from interfaces import IVCardView 

log = logging.getLogger('vs.org')

VC_HEADER = """\
BEGIN:VCARD
VERSION:3.0
PROFILE:VCARD
"""

VC_FOOTER = """\
PRODID:-// VS ORG EMPLOYEE // EMPLOYEE //DE
END:VCARD
"""

from_encoding = 'utf-8'
to_encoding = 'windows-1252'

class VCardView(BrowserView):
    
    implements(IVCardView)
    
    def _u(self, val):
        return unicode(str(val),from_encoding).encode(to_encoding) 

    def _vf(self, val):
        return vformat(self._u(val))

    def getVCard(self):
        """ vCard """

        VF = self._vf # shortcut
        out = StringIO()           

        # extract the vcard relevant data through an IVCardData adapter
        adapter = IVCardData(self.context)
        data = adapter.getVCardData()

        # auf foldLine mit absicht verzichtet ... buggy is das adressbuch von
        # MacOS -> kann keine karte einlesen, in der foldline benutzt wird :(

        # NAME:Hans Mustermann Visitenkarte
        out.write('NAME:%s Vcard\n' % vformat(data['id']))
        # SOURCE
        out.write('SOURCE:%s\n' % data['source'])
        # FN
        out.write('FN;LANGUAGE=de;CHARSET=%s:%s\n' % 
                  (to_encoding, VF(data['vcardname'])))
        # N:nachname;vorname;2.vorname;titel
        content = '%s;%s;;%s' % (VF(data['lastname']), 
                                   VF(data['firstname']), 
                                   VF(data['degree']))
        out.write('N;LANGUAGE=de;CHARSET=%s:%s\n' % (to_encoding, content))
        # SORT-STRING

        if data['lastname']:
            out.write('SORT-STRING:%s\n' % VF(data['lastname']))

        # PHOTO (inline)
        if data['image']:
            encoded_data = base64.encodestring(data['image'])
            out.write('PHOTO;BASE64:\n')
            for line in encoded_data.split('\n'):
                out.write('  ' + line)
            out.write('\n')

        # EMAIL;TYPE=INTERNET
        if data['email']:
            out.write('EMAIL;TYPE=INTERNET:%s\n' % data['email'])

        # URL:http://de.wikipedia.org/
        if data['url']:
            out.write('URL;WORK:%s\n' % data['url'])
        
        # TEL;TYPE=PREF;TYPE=WORK:030-1234567
        if data['phone']:
            out.write('TEL;TYPE=PREF;TYPE=WORK:%s\n' % data['phone'])
            
        # TEL;TYPE=FAX:030-1234567
        if data['fax']:
            out.write('TEL;TYPE=FAX:%s\n' % data['fax'])
        
        # TEL;TYPE=CELL:+49 1234 56789
        if data['mobile']:
            out.write('TEL;TYPE=CELL:%s\n' % data['mobile'])
        
        # TITLE:SACHBEREICH
        # ROLE:FUNKTION)
        if data['position']:
            content = VF(data['position'])
            out.write('ROLE;LANGUAGE=de;CHARSET=%s:%s\n' % (to_encoding, content))

        # ORG;LANGUAGE=de;CHARSET=utf-8:einrichtung
        if data['institution']:
            content = VF(data['institution'])
            out.write('ORG;LANGUAGE=de;CHARSET=%s:%s\n' % (to_encoding, content))
        
        # REV:2007-01-03T11\:08\:23Z
        date_rev = rfc2445dt(DateTime())
        out.write('REV:%s\n' % (vformat(date_rev) ))

        # NOTE aka Description
        if data['notes']:
            content = '%s\n' % VF(data['notes'])
            out.write('NOTE;LANGUAGE=de;CHARSET=%s:%s' % (to_encoding, content))

        # addresses
        for i, row in enumerate(data.get('addresses', ())):
            content= '%s;;%s;%s;%s;%s;%s' % (VF(row['pobox']), 
                                               VF(row['street']),
                                               VF(row['city']),
                                               VF(row['province']),
                                               VF(row['zipcode']),
                                               VF(row['country'])
                                               )
            if i==0:
                out.write('ADR;CHARSET=%s;TYPE=pref,work:%s\n' % (to_encoding,content))
            else:
                out.write('ADR;CHARSET=%s;TYPE=work:%s\n' % (to_encoding,content))

        return out.getvalue()

    def __call__(self, **kwargs):
        """ vCard output  """
        out = StringIO()
        out.write(VC_HEADER)
        out.write(self.getVCard())
        out.write(VC_FOOTER)
        vcard = out.getvalue()
        self.request.RESPONSE.setHeader('Content-Type', 'text/x-vcard')
        self.request.RESPONSE.setHeader('Content-Length', len(vcard))
        self.request.RESPONSE.setHeader('Content-Disposition', 
                                        'attachment; filename="%s.vcf"' % self.context.getId())
        return n2rn(vcard)

