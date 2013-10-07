#
# Copyright (c) 2013 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#


# import standard packages
import logging
from transaction.interfaces import ITransactionManager
from zope.intid.interfaces import IIntIds
from ztfy.utils.catalog import indexObject

logger = logging.getLogger('ztfy.thesaurus')

# import Zope3 interfaces
from zope.component.interfaces import ISite

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


def evolve(context):
    """Create base_label index in each thesaurus"""
    logger.info("Indexing terms in ZTFY.thesaurus inner catalogs...")
    root_folder = context.connection.root().get(ZopePublication.root_name, None)
    for site in root_folder.values():
        if ISite(site, None) is not None:
            hooks.setSite(site)
            for name, thesaurus in getUtilitiesFor(IThesaurus):
                logger.info("Updating thesaurus: " + name)
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
                ITransactionManager(catalog).commit()
