from Products.CMFCore.utils import getToolByName
import logging
 
PROFILE_ID = 'profile-collective.videolink:default'
def upgrade_to_1500(context):
    # install the company_type index
    logger = logging.getLogger(PROFILE_ID)
    null_upgrade_step(context, logger)
    install_typeinfo(context, "Add custom video view to folders and collections")

def null_upgrade_step(tool):
    """ This is a null upgrade, use it when nothing happens """
    pass

def install_typeinfo(context, loginfo):
    logger = logging.getLogger(PROFILE_ID)
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'typeinfo')
    logger.info("reinstalled typeinfo %s" % loginfo)


def add_catalog_indexes(context, logger=None):
    """Method to add our wanted indexes to the portal_catalog.

    @parameters:

    the plone site and 'logger' is the portal_setup logger.  But
    this method can also be used as upgrade step, in which case
    'context' will be portal_setup and 'logger' will be None.
    """
    if logger is None:
        # Called as upgrade step: define our own logger.
        logger = logging.getLogger(PROFILE_ID)

    # Run the catalog.xml step as that may have defined new metadata
    # columns.  We could instead add <depends name="catalog"/> to
    # the registration of our import step in zcml, but doing it in
    # code makes this method usable as upgrade step as well.  Note that
    # this silently does nothing when there is no catalog.xml, so it                                                                                  
    # is quite safe.
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'catalog')

    catalog = getToolByName(context, 'portal_catalog')
    indexes = catalog.indexes()
    # Specify the indexes you want, with ('index_name', 'index_type')
    wanted = (
              ('company_type', 'KeywordIndex'),
              )
    indexables = []
    for name, meta_type in wanted:
        if name not in indexes:
            catalog.addIndex(name, meta_type)
            indexables.append(name)
            logger.info("Added %s for field %s.", meta_type, name)
    if len(indexables) > 0:
        logger.info("Indexing new indexes %s.", ', '.join(indexables))
        catalog.manage_reindexIndex(ids=indexables)
