# -*- coding: utf-8 -*-
from collective.contentrules.subscription.actions.mail import IMailSubscriptionsAction
from plone.contentrules.engine.interfaces import IRuleStorage
from zope.component import getUtility
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


def SubscriptionRulesVocabularyFactory(context):
    """
    Vocabulary that returns a list of possible subscription rules
    """
    storage = getUtility(IRuleStorage)
    rules = []
    for rule in storage.values():
        for action in rule.actions:
            if IMailSubscriptionsAction.providedBy(action):
                rules.append(SimpleTerm(action.actionUID, action.actionUID, rule.title))
    return SimpleVocabulary(rules)
