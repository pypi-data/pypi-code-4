from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.utils import UniqueObject
from collective.contentrules.subscription import SUBSCRIPTION_TOOL
from persistent.dict import PersistentDict
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from collective.contentrules.subscription import subscriptionMessageFactory as _


class Tool(UniqueObject, SimpleItem):
    """
    Contentrules subscription tool
    """
    id = SUBSCRIPTION_TOOL
    meta_type = 'Contentrules Subscription Tool'
    plone_tool = 1

    def __init__(self):
        self.subscriptions = PersistentDict()

    def registerUser(self, rule_id, email):
        """
        Insert the given email address in the given rule_id
        """
        if not rule_id in self.subscriptions:
            self.subscriptions[rule_id] = [email]
        else:
            if email in self.subscriptions[rule_id]:
                factory = getUtility(IVocabularyFactory,
                                     "contentrules.subscription.vocabularies.SubscriptionRulesVocabulary")
                vocabulary = factory(self)
                rule_term = vocabulary.getTerm(rule_id)
                msg = _('already_subscribed_error',
                        default='The given email is already present for "${title}"',
                        mapping=dict(title=rule_term.title))
                return False, msg
            else:
                self.subscriptions[rule_id].append(email)
        return True, ""

    def getSubscriptions(self):
        """
        Return the list of subscriptions
        """
        return self.subscriptions

    def getActionUIDS(self):
        """
        return a list of email addresses for the given rule_id
        """
        return self.subscriptions.keys()

    def getRegisteredList(self, rule_id):
        """
        return a list of email addresses for the given rule_id
        """
        return self.subscriptions.get(rule_id, [])

InitializeClass(Tool)
