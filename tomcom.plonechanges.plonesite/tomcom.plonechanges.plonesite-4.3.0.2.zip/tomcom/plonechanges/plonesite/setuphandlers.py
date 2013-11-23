# -*- coding: utf-8 -*-
#
#
# Copyright (c) 2008 by []
# Generator: ArchGenXML Version 2.1
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """unknown <unknown>"""
__docformat__ = 'plaintext'



def setup_custom(context):
    portal=context.getSite()
    logging=portal.getBrowser('logging')
    setattr(portal,'_at_uid','root')
    setattr(portal,'_plone.uuid','root')
    portal._p_changed=1
    portal.indexObject()

    portal.getBrowser('logging').log(plonesite='Set uid of Plone Site to "root"')

##code-section FOOT
##/code-section FOOT
