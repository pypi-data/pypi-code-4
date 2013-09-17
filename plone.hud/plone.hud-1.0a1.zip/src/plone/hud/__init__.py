# -*- coding: utf-8 -*-
"""Init and utils."""

from plone import api
from plone.hud.misc import CONFIGLET_CATEGORY
from plone.hud.misc import get_panel_id
from plone.hud.misc import get_panel_label
from plone.hud.misc import PROJECT_NAME
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('plone.hud')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""


def register_hud_panel(name):
    """Register HUD panel by name."""
    config_tool = api.portal.get_tool(name='portal_controlpanel')

    if not config_tool:
        return None

    configlet_id = get_panel_id(name)
    configlet_label = get_panel_label(name)
    configlet = {
        'id': configlet_id,
        'name': configlet_label,
        'action': 'string:${{portal_url}}/{0}'.format(configlet_id),
        'condition': '',
        'category': CONFIGLET_CATEGORY,
        'visible': 1,
        'appId': PROJECT_NAME,
        'permission': 'ManagePortal',
        'imageUrl': ''
    }

    config_tool.registerConfiglet(**configlet)

    return configlet_id


def unregister_hud_panel(name):
    """Unregister HUD panel by the same name used for registering."""
    config_tool = api.portal.get_tool(name='portal_controlpanel')

    if not config_tool:
        return None

    configlet_id = get_panel_id(name)

    config_tool.unregisterConfiglet(configlet_id)

    return configlet_id
