from zope.interface import Interface

class IConnectBrowserView(Interface):
    """Connect Browser View"""

    def upload(self):
        """Upload a file to the zodb"""
