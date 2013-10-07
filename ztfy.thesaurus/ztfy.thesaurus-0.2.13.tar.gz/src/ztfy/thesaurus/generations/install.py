#
# Copyright (c) 2013 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#


# import standard packages
import logging
logger = logging.getLogger('ztfy.thesaurus')

# import Zope3 interfaces
from transaction.interfaces import ITransactionManager
from zope.component.interfaces import ISite
from zope.intid.interfaces import IIntIds

# import local interfaces
from ztfy.thesaurus.interfaces.term import IThesaurusTerm
from ztfy.thesaurus.interfaces.thesaurus import IThesaurus

# import Zope3 packages
from zc.catalog.catalogindex import ValueIndex
from zope.app.publication.zopepublication import ZopePublication
from zope.component import getUtility, getUtilitiesFor
from zope.location import locate
from zope.site import hooks

# import local packages
from ztfy.utils.catalog import indexObject


def evolve(context):
    """Create base_label index in each thesaurus"""
    logger.info("Checking index in ZTFY.thesaurus inner catalog...")
    root_folder = context.connection.root().get(ZopePublication.root_name, None)
    for site in root_folder.values():
        if ISite(site, None) is not None:
            hooks.setSite(site)
            for _name, thesaurus in getUtilitiesFor(IThesaurus):
                catalog = thesaurus.catalog
                if 'base_label' not in catalog:
                    index = ValueIndex('base_label', IThesaurusTerm, field_callable=False)
                    locate(index, catalog, 'base_label')
                    catalog['base_label'] = index
                intids = getUtility(IIntIds)
                for index, term in enumerate(thesaurus.terms.itervalues()):
                    indexObject(term, catalog, 'base_label', intids=intids)
                    if not index % 100:
                        ITransactionManager(catalog).savepoint()
