""" Custom viewlets
"""
from zope.component import queryAdapter
from plone.app.layout.viewlets import common
from zope.component.hooks import getSite
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from eea.alchemy.controlpanel.interfaces import IAlchemySettings

class AlchemyViewlet(common.ViewletBase):
    """ A custom viewlet registered above the body tag to insert alchemy markers
    """
    render = ViewPageTemplateFile('../zpt/viewlet.pt')

    def __init__(self, context, request, view, manager=None):
        super(AlchemyViewlet, self).__init__(context, request, view, manager)
        self._settings = None

    @property
    def settings(self):
        """ Settings
        """
        if self._settings is None:
            site = getSite()
            self._settings = queryAdapter(site, IAlchemySettings)
        return self._settings

    @property
    def available(self):
        """ Condition for rendering of this viewlet
        """
        enabled = self.settings.autoTagging or False
        return enabled
