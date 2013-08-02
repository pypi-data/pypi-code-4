from five import grok
from plone.directives import dexterity, form
from collective.qabank.content.question import IQuestion

grok.templatedir('templates')

class Index(dexterity.DisplayForm):
    grok.context(IQuestion)
    grok.require('zope2.View')
    grok.template('question_view')
    grok.name('view')
