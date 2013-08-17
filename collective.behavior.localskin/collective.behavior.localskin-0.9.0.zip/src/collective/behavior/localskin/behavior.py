# -*- coding: utf-8 *-*
from Products.CMFCore.utils import getToolByName
from collective.behavior.localregistry.proxy import LocalRegistry
from plone.registry.interfaces import IRegistry
from plone.supermodel import model
from z3c.form.interfaces import IEditForm
from zope import schema
from zope.component.hooks import getSite
from zope.globalrequest import getRequest
from zope.component import (
    adapter,
    getUtility,
    queryUtility
)
from zope.interface import (
    implements,
    implementer,
    alsoProvides,
    Interface
)
from plone.autoform.interfaces import IFormFieldProvider
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from collective.behavior.localskin import _


def getSkinNames(context):
    try:
        skins_tool = getToolByName(context, 'portal_skins')
    except AttributeError:
        skins_tool = getToolByName(getSite(), 'portal_skins')
    skins = skins_tool._getSelections().keys()
    terms = map(SimpleTerm, skins)
    terms.insert(0, (SimpleTerm('', '', _(u'No local skin'))))
    return SimpleVocabulary(terms)


class ILocalRegistryDependentFields(Interface):
    """Marker interface for conditionally providing fields for a behavior
    """


class ILocalSkin(model.Schema):

    skinname = schema.Choice(
        title=_(u"Skin name"),
        vocabulary='collective.behavior.localskin.vocabularies.skinnames',
    )

alsoProvides(ILocalSkin, ILocalRegistryDependentFields)


def getMyLocalRegistry(context):
    """Return local registry if and only if its an attribute of the context
    """
    registry = queryUtility(IRegistry, None)
    if registry is None:
        return None
    if not isinstance(registry, LocalRegistry):
        return None
    if registry != getattr(context, 'local_registry', None):
        return None
    return registry


def getMyLocalSettings(context, iface):
    """Return (or create and return) settings for an interface if and only if
    the found local registry is an attribute of the context
    """
    registry = getMyLocalRegistry(context)
    if registry is None:
        return None
    try:
        settings = registry.forInterface(iface)
    except KeyError:
        registry.registerInterface(iface)
        settings = registry.forInterface(iface)
    return settings


def getContextFromRequest(request):
    """Return context extracted from request (after publish traverse)
    """
    published = request.get('PUBLISHED', None)
    context = getattr(published, '__parent__', None)
    if context is None:
        context = request.PARENTS[0]
    return context


@implementer(IFormFieldProvider)
@adapter(ILocalRegistryDependentFields)
def getLocalSkinFormFieldProvider(iface):
    context = getContextFromRequest(getRequest())
    if getMyLocalRegistry(context) is not None:
        return iface
    else:
        return None


class LocalSkin(object):

    implements(ILocalSkin)

    def __init__(self, context):
        self._settings = getMyLocalSettings(context, ILocalSkin)

    def set_skinname(self, value):
        if self._settings:
            self._settings.skinname = value

    def get_skinname(self):
        if self._settings:
            return self._settings.skinname

    skinname = property(get_skinname, set_skinname)


def change_skin(event):
    registry = queryUtility(IRegistry, None)

    # Skip undefined registry
    if not registry:
        return

    # Skip global registry
    if not isinstance(registry, LocalRegistry):
        return

    # Skip unset values
    try:
        settings = registry.forInterface(ILocalSkin)
    except KeyError:
        return

    # Find context
    context = getContextFromRequest(event.request)

    # Skip context, which cannot change skin
    if not hasattr(context, 'changeSkin'):
        return

    # Skip edit forms of objects with ILocalSkin-behavior
    if ILocalSkin(context, None) is not None:
        published = event.request.get('PUBLISHED', None)
        form = getattr(published, 'form', None)
        if IEditForm.implementedBy(form):
            return

    # Get the vocabulary to match against
    vocabulary = getUtility(
        IVocabularyFactory,
        name='collective.behavior.localskin.vocabularies.skinnames'
    )(context)

    # Change valid skinname when possible
    if settings.skinname in vocabulary:
        context.changeSkin(settings.skinname)
