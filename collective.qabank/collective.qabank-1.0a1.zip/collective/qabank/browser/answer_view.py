from five import grok
from plone.directives import dexterity, form
from collective.qabank.content.answer import IAnswer

grok.templatedir('templates')

class Index(dexterity.DisplayForm):
    grok.context(IAnswer)
    grok.require('zope2.View')
    grok.template('answer_view')
    grok.name('view')

