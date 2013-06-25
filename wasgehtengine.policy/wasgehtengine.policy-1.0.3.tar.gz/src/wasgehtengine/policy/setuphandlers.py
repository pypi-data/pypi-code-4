from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage

import string
import random

def generate_passwd(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

def add_user(portal, username, user_full_name, user_email):
    # portal_registration manages new user creation
    regtool = getToolByName(portal, 'portal_registration')
    
    password = generate_passwd()
    
    # This is the minimum required information
    # to create a working member
    properties = {
        'username': username,
        # Full name must always be utf-8 encoded
        'fullname': user_full_name.encode("utf-8"),
        'email': user_email
        }

    try:
        # addMember() returns MemberData object
        member = regtool.addMember(username, password, properties=properties)
    except ValueError, e:
        # Give user visual feedback what went wrong
        IStatusMessage(request).addStatusMessage(_(u"Could not create the user:") + unicode(e), "error")
        return None

def importVarious(context):
    """Miscellanous steps import handle
    """
    
    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a 
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.
    
    if context.readDataFile('wasgehtengine.policy-various.txt') is None:
        return
    
    portal = context.getSite()
    
    add_user(portal, 'osm-venue-importer', 'OpenStreetMap Venue Importer', 'osm-venue-importer@wasgehtengine.org')
    add_user(portal, 'event-importer', 'Event Importer', 'event-importer@wasgehtengine.org')