#!/usr/bin/python
# -*- coding: utf-8 -*-

import grok

from dolmen.forms import crud
from dolmen.app.authentication import ManageUsers, MF as _
from dolmen.authentication import IPrincipalFolder
from dolmen.forms.base import Fields
from grokcore.component import provider
from grokcore.layout import Page

from zeam.form.base.datamanager import makeAdaptiveDataManager
from zope.authentication.interfaces import IAuthentication
from zope.interface import Interface, classProvides
from zope.schema import Tuple, Choice
from zope.component import queryUtility
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import IVocabularyFactory, ISource
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary


class PrincipalFoldersList(SimpleVocabulary):
    classProvides(IVocabularyFactory)

    def __init__(self, pau):
        terms = [SimpleTerm(
            value=p.__name__, token=p.__name__,
            title="%s (%s)" % (p.__name__, p.title or p.__name__))
                 for p in pau.values() if IPrincipalFolder.providedBy(p)]
        super(PrincipalFoldersList, self).__init__(terms)


@provider(IContextSourceBinder)
def folders_source(context):
    # Provides some pluggability. Do we need this ?
    folders = queryUtility(
        IVocabularyFactory, name=u'PrincipalFolders')
    if folders is None:
        return PrincipalFoldersList(context)
    return folders(context)


class IActiveFolders(Interface):
    """Principal folders management.
    """
    activeFolders = Tuple(
        title=_(u"Active authentication sources"),
        value_type=Choice(source=folders_source),
        default=tuple())


class ActiveFoldersChoice(grok.Adapter):
    grok.implements(IActiveFolders)
    grok.context(IAuthentication)

    @apply
    def activeFolders():
        """Property allowing to access and set the active
        PrincipalFolders of the adapted PAU.
        """
        def fget(self):
            return tuple(
                (p for p in self.context.authenticatorPlugins
                 if IPrincipalFolder.providedBy(self.context.get(p))))

        def fset(self, values):
            auths = set(self.context.authenticatorPlugins)
            folders = set(
                (p.__name__ for p in self.context.values()
                 if IPrincipalFolder.providedBy(p)))

            self.context.authenticatorPlugins = (
                tuple(auths.difference(folders)) + values)

        return property(fget, fset)


class ManageAuth(Page):
    grok.name('index')
    grok.context(IAuthentication)
    grok.require(ManageUsers)


class AuthSources(Page):
    grok.title(_("Authentication sources"))
    grok.context(IAuthentication)
    grok.require(ManageUsers)

    def update(self):
        self.folders = self.context.authenticatorPlugins
        self.credentials = self.context.credentialsPlugins


class PAUPreferences(crud.Edit):
    grok.name('authenticators')
    grok.context(IAuthentication)
    grok.require(ManageUsers)

    fields = Fields(IActiveFolders)
    dataManager = makeAdaptiveDataManager(IActiveFolders)
    label = _(u"Edit the authentication sources")
