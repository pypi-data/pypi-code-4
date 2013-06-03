################################################################
# vs.org (C) 2011, Veit Schiele
################################################################

# $Id$

import re

from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import View
from compatible import atapi 

from .. import orgMessageFactory as _

class NumbersMixin(object):

    security = ClassSecurityInfo()

    security.declareProtected(View, 'getNumbersFiltered')
    def getNumbersFiltered(self):
        return [d for d in self.getNumbers() if d['number']]

    def _getFirstNumber(self, type='phone'):
        for d in self.getNumbers():
            if d['type'] == type:
                return d['number']
        return None

    security.declareProtected(View, 'getTelephone')
    def getTelephone(self):
        """ return Telephone from DGF """
        return self._getFirstNumber('phone')

    security.declareProtected(View, 'getMobile')
    def getMobile(self):
        """ return Mobile from DGF """
        return self._getFirstNumber('mobile')

    security.declareProtected(View, 'getFax')
    def getFax(self):
        """ return Mobile from DGF """
        return self._getFirstNumber('fax')

    security.declareProtected(View, 'getNumbersByType')
    def getNumbersByType(self, type='phone', do_filter=True):
        """ Return all numbers for a given type.

            If 'do_filter' is set: expose only numbers that are either
            'externally_visible' or when the member has on of the roles
            Authenticated or Member.
        """

        mt = getToolByName(self, 'portal_membership')
        member = mt.getAuthenticatedMember()
        roles = member.getRolesInContext(self)
        view_internal_numbers = False
        if 'Authenticated' in roles or 'Member' in roles:
            view_internal_numbers = True
        result = list()
        for d in self.getNumbers():
            # Check DGF flag (''==only internally visible, '1'==externally visible)
            number_is_internal = (d.get('externally_visible', '')=='')
            if d['type'] == type and d['number']:
                if do_filter:
                    if not number_is_internal or (number_is_internal and view_internal_numbers):

                        result.append(d['number'])
                else:
                    result.append(d['number'])

        return result

    security.declareProtected(View, 'getNumberTypes')
    def getNumberTypes(self):
        """ return all number types """
        result = list()
        for d in self.getNumbers():
            if not d['type'] in result and d['number']:
                result.append(d['type'])
        return result

    def validate_numbers(self, rows):
        """ Numbers validation """

        pprop = getToolByName(self, 'portal_properties')
        vsprop = getToolByName(pprop, 'vsorg_properties')
        number_regex = re.compile(vsprop.numberRegex)
        for d in rows:
            if not number_regex.match(d['number']):
                return _('Invalid number: %s' % d['number'])

    security.declarePublic('getNumbersVocabulary')
    def getNumbersVocabulary(self):
        """return number vocabulary for DGF (managed through ATVocabularyManager)"""
        vocab_tool = getToolByName(self, 'portal_vocabularies')
        vocab = vocab_tool[self.numbers_vocabulary].getVocabularyDict()
        lst = list()
        for k,v in vocab.items(): 
            lst.append((k, v))
        return atapi.DisplayList(lst)
