from Products.ATContentTypes.config import HAS_LINGUA_PLONE
from Products.CMFCore.utils import ContentInit
from redturtle.entiterritoriali.config import PROJECTNAME
if HAS_LINGUA_PLONE:
    from Products.LinguaPlone.public import process_types
    from Products.LinguaPlone.public import listTypes
else:
    from Products.Archetypes.atapi import process_types
    from Products.Archetypes.atapi import listTypes

from redturtle.entiterritoriali.vocabulary import SQLite3Vocab

EntiVocabulary = SQLite3Vocab()
_all_province = EntiVocabulary.allProvince()
_all_regioni = EntiVocabulary.allRegioni()
_all_comuni = EntiVocabulary.allComuni()


def initialize(context):

    import EntiCriteria
    listOfTypes = listTypes(PROJECTNAME)
    content_types, constructors, ftis = process_types(
        listOfTypes,
        PROJECTNAME)

    from redturtle.entiterritoriali.config import default_permission

    allTypes = zip(content_types, constructors)
    for atype, constructor in allTypes:
        kind = "%s: %s" % (PROJECTNAME, atype.archetype_name)
        ContentInit(
            kind,
            content_types      = (atype,),
            permission         = default_permission,
            extra_constructors = (constructor,),
            ).initialize(context)
