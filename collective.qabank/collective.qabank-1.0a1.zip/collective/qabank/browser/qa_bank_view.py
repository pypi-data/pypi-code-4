from five import grok
from plone.directives import dexterity, form
from collective.qabank.content.qa_bank import IQABank

grok.templatedir('templates')

class Index(dexterity.DisplayForm):
    grok.context(IQABank)
    grok.require('zope2.View')
    grok.template('qa_bank_view')
    grok.name('view')

