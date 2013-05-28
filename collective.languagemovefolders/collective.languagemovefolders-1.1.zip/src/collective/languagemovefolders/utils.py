# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from AccessControl import Unauthorized
from Products.CMFCore.permissions import ModifyPortalContent
import logging


logger = logging.getLogger('collective.languagemovefolders')


def move_all(portal):
    sm = getSecurityManager()
    if not sm.checkPermission(ModifyPortalContent, portal):
        error = 'You need ModifyPortalContent permissionto execute some_\
                function'
        raise Unauthorized(error)

    portal_languages = portal.portal_languages
    langs = portal_languages.getAvailableLanguages()
    results = []
    for lang in langs:
        if not getattr(portal, lang, None):
            message = u"{0} language folder doesn't exists,<br> please call \
                the LinguaPlone view: <a href='{1}/@@language-setup-folders'>\
                    @@language-setup-folders</a>".format(
                        lang, portal.absolute_url())
            logger.info(message)
            return message
        else:
            # XXX: copy portlets
            folder_language = getattr(portal, lang)
            objects = prepare_moving(portal, langs)
            for obj in objects[lang]:
                folder_language.manage_pasteObjects(
                               obj.aq_parent.manage_cutObjects(obj.getId()))
                message = "{0}: {1} was moved".format(lang, obj.getId())
                logger.info(message)
                results.append(message)

    return "<br />".join(results)


def prepare_moving(site, langs):
    """ return a dict with languages as key (fr, en, nl, ...) and object,
    in language of the key, which are in the root of the Plone site, as values.
    """
    objects = {}
    for lang in langs:
        objects[lang] = []
    root_objects = site.contentValues()
    for root_object in root_objects:
        if root_object.id not in langs.keys():
            if root_object.getLanguage():
                if root_object.getLanguage() in objects.keys():
                    objects[root_object.getLanguage()].append(root_object)
                else:
                    logger.warn("Object {0} is not in site languages, \
                            object is in {1}".format(
                        root_object.id, root_object.getLanguage()))

            else:
                logger.warn("Object {0} has no language".format(
                    root_object.id))
    return objects
