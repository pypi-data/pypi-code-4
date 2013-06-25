# -*- coding: utf-8 -*-
import logging
from zope.app.component.hooks import getSite
from zope.i18nmessageid import MessageFactory
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
_ = MessageFactory("ityou.astream")


def isProductAvailable(product):
    """Check if a product is installed and return True, 
    else return False
    """
    qui = getSite().portal_url.getPortalObject().portal_quickinstaller
    installed_products = qui.listInstalledProducts()
    for prod in installed_products:
        if prod["id"] == product and prod["status"] == "installed":
            return True
    return False


def getNotifyDBApi():
    """Loads Notify DBApi Function
    Returns False if the product is not installed
    """
    dbapi_notify = False
    plone = getSite()
    
    qui = plone.portal_url.getPortalObject().portal_quickinstaller
    installed_products = qui.listInstalledProducts()
    
    for product in installed_products:
        if product["id"] == "ityou.notify" and product["status"] == "installed":
            try:
                from ityou.notify.dbapi import DBApi
                from ityou.notify.interfaces import INotifySettings
                if getUtility(IRegistry).forInterface(INotifySettings).astream_notifications_active:
                    dbapi_notify = DBApi()
                else:
                    logging.info("ityou.astream says: ITYOU Notify App is deactivated - No emails will be send")
            except:
                logging.info("ityou.astream says: ITYOU Notify App not installed - No emails will be send")
            
    return dbapi_notify


def getWhoIsOnlineDBApi():
    """Loads the WhoIsOnline DBApi if exists or
    return False if ityou.whoisonline is not instalt
    """

    dbapi_whoisonline = False
    plone = getSite()

    qui = plone.portal_url.getPortalObject().portal_quickinstaller
    installed_products = qui.listInstalledProducts()
    
    for product in installed_products:
        if product["id"] == "ityou.whoisonline" and product["status"] == "installed":
            try:
                from ityou.whoisonline.dbapi import DBApi
                from ityou.whoisonline.interfaces import IWhoIsOnlineSettings
                if getUtility(IRegistry).forInterface(IWhoIsOnlineSettings).max_users:
                    dbapi_whoisonline = DBApi()
                else:
                    logging.info("ityou.astream says: ITYOU WhoIsOnline App is deactivated - No emails will be send")
            except:
                logging.info("ityou.astream says: ITYOU WhoIsOnline App not installed - No emails will be send")
            
    return dbapi_whoisonline



def initialize(context):
    """Initializer called when used as a Zope 2 product."""

