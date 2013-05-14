import logging
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('ityou.whoisonline')


#ityou.imessage
try:
    from ityou.imessage.dbapi import DBApi
    from ityou.imessage.portlets.utils import InstantMessageUtils  
    db_imessage = DBApi()
    imessage_utils = InstantMessageUtils()
except:
    db_imessage = None
    imessage_utils = None

#ityou.extuserprofile
try:
    import ityou.extuserprofile
    logging.info("ityou.intranet says: extuserprofile  App is installed - Great!")
    ityou_extuserprofile_installed = True
except:
    ityou_extuserprofile_installed = False
    logging.info("ityou.intranet says: Unfortunately extuserprofile App not installed - You will not see extended user profiles")


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
