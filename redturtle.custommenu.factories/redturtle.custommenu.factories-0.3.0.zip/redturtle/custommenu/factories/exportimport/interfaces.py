from zope.interface import Interface

class ICustomMenuFactoriesAssignment(Interface):
    """A component that support custom menu factories
    """

    def disable(self):
        """Disable custom menu factories
        """

    def inherit(self):
        """True if the custom menu factories is inheriting settings
        """

    def setInherit(self, inherit):
        """Change the inherit value
        """

    def addMenuEntry(self, item):
        """Add new custom menu entry
        """

    def removeMenuEntry(self, item):
        """Remove a custom menu entry
        """

    def listMenuEntry(self):
        """Return a list with the current menu entries
        """
