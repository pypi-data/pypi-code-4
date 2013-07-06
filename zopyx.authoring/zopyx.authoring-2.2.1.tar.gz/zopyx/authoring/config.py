#####################################################################
# zopyx.authoring
# (C) 2010, ZOPYX Limited, D-72070 Tuebingen. All rights reserved
#####################################################################

"""Common configuration constants """

import os

PROJECTNAME = 'zopyx.authoring'

ADD_PERMISSIONS = {
    # -*- extra stuff goes here -*-
    'AuthoringCalibreProfile': 'zopyx.authoring: Add AuthoringCalibreProfile',
    'AuthoringContentAggregator': 'zopyx.authoring: Add AuthoringContentAggregator',
    'AuthoringPublishedDocument': 'zopyx.authoring: Add AuthoringPublishedDocument',
    'AuthoringConversionsCollection': 'zopyx.authoring: Add AuthoringConversionsCollection',
    'AuthoringCoverPage': 'zopyx.authoring: Add AuthoringCoverPage',
    'AuthoringContentPage': 'zopyx.authoring: Add AuthoringContentPage',
    'AuthoringConversionFolder': 'zopyx.authoring: Add AuthoringConversionFolder',
    'AuthoringContentsFolder': 'zopyx.authoring: Add AuthoringContentsFolder',
    'AuthoringTemplate': 'zopyx.authoring: Add AuthoringTemplate',
    'AuthoringTemplatesFolder': 'zopyx.authoring: Add AuthoringTemplatesFolder',
    'AuthoringImageResource': 'zopyx.authoring: Add AuthoringImageResource',
    'AuthoringStylesheet': 'zopyx.authoring: Add AuthoringStylesheet',
    'AuthoringBinaryResource': 'zopyx.authoring: Add AuthoringBinaryResource',
    'AuthoringMasterTemplate': 'zopyx.authoring: Add AuthoringMasterTemplate',
    'AuthoringContentFolder': 'zopyx.authoring: Add AuthoringContentFolder',
    'AuthoringProject': 'zopyx.authoring: Add AuthoringProject',
}


DEPENDENCIES = [
    'Products.DataGridField',
#    'Products.ImageEditor',
]

PUBLISHED_DOCUMENT_CSS = """
#content {
    counter-reset: c1 %(chapter_number)d table-counter %(table_counter)d  image-counter %(image_counter)d;
}
"""

CALIBRE_DEFAULT_OPTIONS = [
    dict(name='--level1-toc', value="//*[name()='h1']"),
    dict(name='--level2-toc', value="//*[name()='h2']"),
    dict(name='--level3-toc', value="//*[name()='h3']"),
    dict(name='--page-breaks-before', value="//*[name()='h1' or name()='h2']"),
    dict(name='--title', value='%(title)s'),
    dict(name='--authors', value='%(authors)s')
]

CONVERSION_SERVER_URL = os.environ.get('SMARTPRINTNG_SERVER', 'http://localhost:6543')
