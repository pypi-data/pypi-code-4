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


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
