# -*- coding: utf-8 -*-
# $Id: upgrades.py 9248 2009-11-11 09:51:09Z glenfant $
"""GenericSetup upgrade steps"""

try:
    from zope.component.hooks import getSite
    getSite  # Pyflakes
except ImportError:  # Plone < 4.3
    from zope.app.component.hooks import getSite
from Products.CMFCore.utils import getToolByName

###
## Utilities
###


class NotInstalledComponent(LookupError):
    def __init__(self, cpt_name):
        self.cpt_name = cpt_name
        return

    def __str__(self):
        msg = ("Component '%s' is not installed in this site."
               " You can't run its upgrade steps."
               % self.cpt_name)
        return msg


class IfInstalled(object):
    def __init__(self, prod_name='SmartColorWidget'):
        """@param prod_name: as shown in quick installer"""
        self.prod_name = prod_name

    def __call__(self, func):
        """@param func: the decorated function"""
        def wrapper(setuptool):
            qi = getSite().portal_quickinstaller
            installed_ids = [p['id'] for p in qi.listInstalledProducts()]
            if self.prod_name not in installed_ids:
                raise NotInstalledComponent(self.prod_name)
            return func(setuptool)
        wrapper.__name__ = func.__name__
        wrapper.__dict__.update(func.__dict__)
        wrapper.__doc__ = func.__doc__
        wrapper.__module__ = func.__module__
        return wrapper

if_scw_instaled = IfInstalled()

###
## Upgrade steps handlers
###


@if_scw_instaled
def steps_1_0_3_to_1_1_0(setuptool):
    """Removing CMF skins layer and adding browserlayer marker"""
    removeSkinsLayer(setuptool)
    registerBrowserLayer(setuptool)
    return

###
## Sub steps
###


def removeSkinsLayer(setuptool):
    """Removing CMF skins layer"""
    to_delete = 'smartcolorwidget'
    portal = getSite()
    portal_skins = getToolByName(portal, 'portal_skins')
    if to_delete in portal_skins.objectIds():
        portal_skins._delObject(to_delete)
        # Removing from portal_skins properties
        for skin in portal_skins.selections.keys():
            values = portal_skins.selections[skin].split(',')
            values.remove(to_delete)
            portal_skins.selections[skin] = ','.join(values)
    return


def registerBrowserLayer(setuptool):
    """Adding browserlayer marker"""
    setuptool.runImportStepFromProfile(
        'profile-Products.SmartColorWidget:default',
        'browserlayer')
    return
