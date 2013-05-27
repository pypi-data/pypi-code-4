import logging
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from plone.registry.interfaces import IRegistry
from plone.browserlayer import utils

logger = logging.getLogger('Plone')


def remove_old_browserlayer(setuptool):
    """
    Remove IAddthisBrowserLayer so that we can replace it with
    IAddThisBrowserLayer to be in line with rest of the naming
    conventions.
    """
    try:
        utils.unregister_layer('collective.addthis')
        logger.info('Unregistered old browserlayer')
    except KeyError, e:
        logger.error(str(e))


def migrate_controlpanel(setuptool):
    tools = queryMultiAdapter(
        (setuptool, setuptool.REQUEST), name="plone_tools")
    registry = queryUtility(IRegistry)
    BASE = 'collective.addthis.interfaces.IAddThisSettings.%s'
    rec = registry.records
    portal_properties = tools.properties()
    props = portal_properties.addthis_properties

    addthis_url = getattr(props, 'addthis_url', None)
    if addthis_url:
        account = addthis_url.split('username=')
        if len(account) > 1:
            rec[BASE % 'addthis_account_name'].value = unicode(account[-1])

    chicklets = getattr(props, 'addthis_chicklets', [])
    if chicklets:
        chicklets = [unicode(chicklet) for chicklet in chicklets]
        rec[BASE % 'addthis_chicklets'].value = chicklets

    portal_properties.manage_delObjects('addthis_properties')
    from Products.CMFCore.utils import getToolByName
    cp = getToolByName(setuptool, 'portal_controlpanel')
    cp.unregisterConfiglet('setAddThisSettings')

    logger.info("Migrated addthis controlpanel settings.")


def run_import_steps(setuptool):
    setuptool.runAllImportStepsFromProfile(
        'profile-collective.addthis:upgrade_1000_to_1001')
    logger.info('Ran all GS import steps for collective.addthis.')
