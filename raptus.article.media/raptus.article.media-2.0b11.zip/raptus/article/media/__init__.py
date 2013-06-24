"""Main product initializer
"""
from raptus.article.media import config

from Products.Archetypes import atapi
from Products.CMFCore import utils as cmfutils

def initialize(context):
    from content import video, videoembed, audio

    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes(config.PROJECTNAME),
        config.PROJECTNAME)

    for atype, constructor in zip(content_types, constructors):
        cmfutils.ContentInit("%s: %s" % (config.PROJECTNAME, atype.portal_type),
            content_types      = (atype,),
            permission         = config.ADD_PERMISSION[atype.portal_type],
            extra_constructors = (constructor,),
            ).initialize(context)

