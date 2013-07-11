""" Add countries_mapping vocabulary
"""
from Products.ATVocabularyManager.utils.vocabs import createSimpleVocabs
from Products.CMFCore.utils import getToolByName
import logging

logger = logging.getLogger(__name__)


def install_countries_map_vocabulary(context):
    """ See IVocabularyFactory interface
    """
    atvm = getToolByName(context, "portal_vocabularies")

    countries_id = "countries_mapping"
    countries = {countries_id: (
        ("Czechia", "Czech Republic"),
        ("Macedonia", "Macedonia (FYR)"),
        ("Kosovo", "Kosovo (UNSCR 1244/99)")
    )}

    if not atvm.get(countries_id):
        createSimpleVocabs(atvm, countries)
        atvm[countries_id].setTitle("EEA Custom Country Name Mappings")
        logger.info("Added EEA Custom Country Name Mappings vocabulary")
    else:
        logger.info("Already added EEA Custom Country Name Mappings vocabulary")
