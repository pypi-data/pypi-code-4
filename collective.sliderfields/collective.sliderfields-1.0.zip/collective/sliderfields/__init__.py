from zope.interface import implements
from Products.CMFQuickInstallerTool.interfaces import INonInstallable
from five import grok
from collective.grok import gs
from zope.i18nmessageid import MessageFactory

# Set up the i18n message factory for our package
MessageFactory = MessageFactory('collective.sliderfields')

_ = MessageFactory

class HiddenProducts(grok.GlobalUtility):
    """This hides the upgrade profiles from the quick installer tool."""
    implements(INonInstallable)
    grok.name('collective.sliderfields.upgrades')

    def getNonInstallableProducts(self):
        return [
            'collective.sliderfields.upgrades',
        ]

gs.profile(name=u'default',
           title=u'collective.sliderfields',
           description=_(u''),
           directory='profiles/default')
