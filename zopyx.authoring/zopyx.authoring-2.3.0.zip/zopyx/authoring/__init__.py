#####################################################################
# zopyx.authoring
# (C) 2010, ZOPYX Limited, D-72070 Tuebingen. All rights reserved
#####################################################################

"""Main product initializer
"""

from zope.i18nmessageid import MessageFactory
from zopyx.authoring import config

from Products.Archetypes import atapi
from Products.CMFCore import utils
from Products.CMFCore.permissions import setDefaultRoles

# Define a message factory for when this product is internationalised.
# This will be imported with the special name "_" in most modules. Strings
# like _(u"message") will then be extracted by i18n tools for translation.

authoringMessageFactory = MessageFactory('producepublish')

def initialize(context):
    """Initializer called when used as a Zope 2 product.

    This is referenced from configure.zcml. Regstrations as a "Zope 2 product"
    is necessary for GenericSetup profiles to work, for example.

    Here, we call the Archetypes machinery to register our content types
    with Zope and the CMF.
    """

    # Retrieve the content types that have been registered with Archetypes
    # This happens when the content type is imported and the registerType()
    # call in the content type's module is invoked. Actually, this happens
    # during ZCML processing, but we do it here again to be explicit. Of
    # course, even if we import the module several times, it is only run
    # once.

    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes(config.PROJECTNAME),
        config.PROJECTNAME)

    # Now initialize all these content types. The initialization process takes
    # care of registering low-level Zope 2 factories, including the relevant
    # add-permission. These are listed in config.py. We use different
    # permissions for each content type to allow maximum flexibility of who
    # can add which content types, where. The roles are set up in rolemap.xml
    # in the GenericSetup profile.

    for atype, constructor in zip(content_types, constructors):
        utils.ContentInit('%s: %s' % (config.PROJECTNAME, atype.portal_type),
            content_types      = (atype,),
            permission         = config.ADD_PERMISSIONS[atype.portal_type],
            extra_constructors = (constructor,),
            ).initialize(context)

for id, permission in config.ADD_PERMISSIONS.items():
    setDefaultRoles(permission, ('Manager', 'Owner'))

# activate monkey patches
import patches

# check if ghostscript is installed
import util
from logger import LOG
if util.checkCommand('gs'):
    HAVE_GHOSTSCRIPT = True
    LOG.info('Ghostscript is installed - good!')
else:
    HAVE_GHOSTSCRIPT = False
    LOG.warn('Ghostscript is not installed - bad (needed for PDF optimization)')

if util.checkCommand('tidy'):
    HAVE_TIDY = True
    LOG.info('Tidy is installed - good!')
else:
    HAVE_TIDY = False
    LOG.warn('Tidy is not installed - bad (needed for DOC(X) import)')

if util.checkCommand('curl'):
    HAVE_CURL = True
    LOG.info('Curl is installed - good!')
else:
    HAVE_CURL = False
    LOG.warn('CURL is not installed - bad (needed for DOC(X) import)')

from config import CONVERSION_SERVER_URL
LOG.info('Using conversion server at %s' % CONVERSION_SERVER_URL)

