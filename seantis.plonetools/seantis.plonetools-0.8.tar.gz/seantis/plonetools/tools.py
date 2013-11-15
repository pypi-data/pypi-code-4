import sys
import os.path
import time

from functools import partial, wraps

from App.config import getConfiguration

from plone import api
from plone.dexterity.fti import (
    register as register_dexterity_type,
    DexterityFTI
)
from plone.dexterity.interfaces import IDexterityFTI
from Products.ZCatalog.interfaces import ICatalogBrain
from Products.PortalTransforms.transforms.safe_html import scrubHTML

from zope.component import getMultiAdapter
from zope.component.hooks import getSite
from zope.component import getUtility, getAllUtilitiesRegisteredFor
from zope.component.interfaces import ComponentLookupError
from zope.schema import getFields
from zope import i18n


import pyuca

allkeys = os.path.join('/'.join(os.path.split(__file__)[:-1]), 'allkeys.txt')
collator = pyuca.Collator(allkeys)


def public(f):
    """ Use a decorator to avoid retyping function/class names.

      * Based on an idea by Duncan Booth:
      http://groups.google.com/group/comp.lang.python/msg/11cbb03e09611b8a
      * Improved via a suggestion by Dave Angel:
      http://groups.google.com/group/comp.lang.python/msg/3d400fb22d8a42e1
    """
    all = sys.modules[f.__module__].__dict__.setdefault('__all__', [])
    if f.__name__ not in all:  # Prevent duplicates if run from an IDE.
        all.append(f.__name__)
    return f


@public
def safe_html(html):
    """ Returns the given html without dangerous elements like <script/>. The
    result will still contain html however, not replacments like '&gt;'.

    """
    return scrubHTML(html, raise_error=False)


@public
def get_parent(obj):
    """ Gets the parent of the obj or brain. The result is of the same type
    as the parameter given.

    """

    if ICatalogBrain.providedBy(obj):
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog(
            path={'query': '/'.join(obj.getPath().split('/')[:-1])}
        )
        return brains[0]
    else:
        return obj.aq_inner.aq_parent


@public
def is_existing_portal_type(portal_type):
    """ Return True if the given portal_type can be looked up. """

    try:
        getUtility(IDexterityFTI, portal_type)
    except ComponentLookupError:
        return False

    return True


@public
def get_type_info_by_behavior(behavior):
    """ Returns a list of Dexterity ftis with the given behavior enabled. """

    ftis = getAllUtilitiesRegisteredFor(IDexterityFTI)
    return [fti for fti in ftis if behavior in fti.behaviors]


@public
def get_type_info_by_schema(schema):
    """ Returns a list of Dexterity ftis using the given schema. """

    ftis = getAllUtilitiesRegisteredFor(IDexterityFTI)
    return [fti for fti in ftis if schema == fti.lookupSchema()]


@public
def get_schema_from_portal_type(portal_type):
    """ Get the schema from a portal type. """

    fti = getUtility(IDexterityFTI, portal_type)
    return fti.lookupSchema()


@public
def order_fields_by_schema(fields, schema):
    """ Gets the order of the given scheman and orders the given fields by
    that order. If a field is not found in the schema it is added at the end.

    """

    order = dict((key, f.order) for key, f in getFields(schema).items())
    return sorted(fields, key=lambda field: order.get(field, sys.maxint))


@public
def add_attribute_to_metadata(attribute):
    """ Adds the given attribute to the metadata in the portal catalog. If
    the attribute is alredy there function silently skips it.

    """
    zcatalog = api.portal.get_tool('portal_catalog')._catalog

    if attribute not in zcatalog.schema:
        zcatalog.addColumn(attribute)


@public
def get_brain_by_object(obj):
    """ The inverse of getObject. """
    catalog = api.portal.get_tool('portal_catalog')

    return catalog(path={'query': '/'.join(obj.getPhysicalPath())})[0]


@public
def in_debug_mode():
    """ What you think it is. """
    return getConfiguration().debug_mode


@public
def add_new_dexterity_type(name, **kwargs):
    """ Adds a new dexterity type the same way Dexterity does it internally,
    when using the form. The difference is that this function does not
    assume any defaults and creates the types with the parameters given.

    Behaviors may be given as a list (Dexterity needs a multiline string).
    """
    new_type = DexterityFTI(name)
    kwargs['klass'] = 'plone.dexterity.content.Container'

    if 'behaviors' in kwargs:
        if isinstance(kwargs['behaviors'], list):
            kwargs['behaviors'] = '\n'.join(kwargs['behaviors'])

    new_type.manage_changeProperties(
        **kwargs
    )

    types = api.portal.get_tool('portal_types')
    types._setObject(new_type.id, new_type)

    register_dexterity_type(new_type)

    return new_type


@public
def invert_dictionary(dictionary):
    """ Inverts a dictionary as follows:

    {
        1: 'x',
        2: 'x',
        3: 'y'
    }

    ->

    {
        'x': [1, 2],
        'y': [3]
    }

    """
    inverted = {}

    for k, v in dictionary.iteritems():
        inverted[v] = inverted.get(v, [])
        inverted[v].append(k)

    return inverted


@public
def get_current_language(request):
    """ Returns the current language of the request. """
    portal_state = getMultiAdapter(
        (getSite(), request), name=u'plone_portal_state'
    )
    return portal_state.language()


@public
def translator(request, domain=None):
    """ Returns a function which takes a single string and translates it using
    the curried language of the request

    """

    # xx-xx languages will not work here, though they work when Plone does
    # it in a template. For now it does not matter as we have no country
    # specific translation available
    lang = get_current_language(request).split('-')[0]

    return partial(i18n.translate, target_language=lang, domain=domain)


@public
def unicode_collate_sortkey(case_sensitive=True):
    """ Returns a sort function to sanely sort unicode values.

    A more exact solution would be to use pyUCA but that relies on an external
    C Library and is more complicated

    See:
    http://stackoverflow.com
    /questions/1097908/how-do-i-sort-unicode-strings-alphabetically-in-python
    http://en.wikipedia.org/wiki/ISO_14651
    http://unicode.org/reports/tr10/
    http://pypi.python.org/pypi/PyICU
    http://jtauber.com/blog/2006/01/27/python_unicode_collation_algorithm/
    https://github.com/href/Python-Unicode-Collation-Algorithm

    """

    return collator.sort_key


@public
def profile(fn):
    """ Naive profiling of a function.. on unix systems only. """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.time()

        result = fn(*args, **kwargs)
        print fn.__name__, 'took', (time.time() - start) * 1000, 'ms'

        return result

    return wrapper
