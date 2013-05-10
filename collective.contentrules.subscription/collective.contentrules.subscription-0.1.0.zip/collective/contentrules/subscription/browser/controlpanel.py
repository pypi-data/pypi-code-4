from Products.Five import BrowserView
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from collective.contentrules.subscription import subscriptionMessageFactory as _


class SubscriptionsControlPanel(BrowserView):
    """Vista dei cercatori"""

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.subscription_vocab = self.getSubscriptionsVocab()
        self.tool = getToolByName(self.context,
                                  'contentrules_subscription_tool')

    def getSubscriptionsVocab(self):
        factory = getUtility(IVocabularyFactory,
                             "contentrules.subscription.vocabularies.SubscriptionRulesVocabulary")
        return factory(self.context)

    def __call__(self):
        """
        """
        if not self.request.form.get('form.button.Update', ''):
            return self.index()
        return self.updateSubscriptions()

    def getSubscriptions(self):
        """
        Return the subscriptions dict
        """
        return self.tool.getSubscriptions()

    def getRuleTitle(self, actionUID):
        """
        Return the rule title for a given actionUID
        """
        try:
            term = self.subscription_vocab.getTermByToken(actionUID)
            return term.title
        except LookupError:
            return actionUID
        return actionUID

    def updateSubscriptions(self):
        """
        Update subscriptions in the tool with the values in the request
        """
        subscriptions = self.getSubscriptions()
        for key in subscriptions.keys():
            if key in self.request.form:
                new_values = self.request.form.get(key, [])
                if new_values:
                    subscriptions[key] = new_values
            else:
                del subscriptions[key]
        IStatusMessage(self.request).addStatusMessage(_(u"Subscriptions updated"), "info")
        root = self.context.portal_url()
        self.request.RESPONSE.redirect('%s/@@contentrules-subscription-controlpanel' % root)
