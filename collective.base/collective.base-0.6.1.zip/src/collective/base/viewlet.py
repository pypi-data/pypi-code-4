from collective.base.interfaces import IViewlet
from plone.app.layout.viewlets.common import ViewletBase
from zope.interface import implements


class Viewlet(ViewletBase):
    """Base viewlet"""
    implements(IViewlet)

    def _handle_repeated(self, item):
        raise NotImplementedError('Handle item')

    def repeated(self, item=None):
        """Renders viewlet with argument

        :rtype: unicode
        """
        self._handle_repeated(item)
        return self.render()

    def available(self):
        """Returns True or False

        :rtype: bool
        """
        return True
