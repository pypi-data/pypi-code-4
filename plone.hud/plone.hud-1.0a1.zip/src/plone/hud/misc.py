# -*- coding: utf-8 -*-
"""Misc functions and global constants."""

CONFIGLET_CATEGORY = 'HUD'
PROJECT_NAME = 'plone.hud'
SETTINGS_NAME = 'Settings'


def normalize_name(name):
    result = ""
    for c in name:
        if c in [chr(32), '_']:
            c = '_'
        elif not str.isalnum(c):
            continue
        result += c
    return result.lower()


def get_panel_id(name):
    """Get HUD panel id from name.

    This function is used so the
    registering of HUD panels uses the same id as unregistering,
    both of those functions have only name parameter for simplicity
    and both functions need the same panel id therefore this function
    along with the normalize_name function are necessary.
    """
    return "hud_{0}".format(normalize_name(name))

SETTINGS_ID = get_panel_id(SETTINGS_NAME)


def get_panel_label(name):
    return u"HUD {0}".format(name)

SETTINGS_LABEL = get_panel_label(SETTINGS_NAME)
