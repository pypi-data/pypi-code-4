from five import grok

from zope.interface import implements

from plone.dexterity.content import Item
from plone.dexterity.schema import DexteritySchemaPolicy

from collective.local.sentmail.interfaces import ISentMail


class SentMail(Item):
    implements(ISentMail)


class SentMailSchemaPolicy(grok.GlobalUtility, DexteritySchemaPolicy):
    """Schema policy for SentMail content type"""

    grok.name("schema_policy_sent_mail")

    def bases(self, schemaName, tree):
        return (ISentMail,)
