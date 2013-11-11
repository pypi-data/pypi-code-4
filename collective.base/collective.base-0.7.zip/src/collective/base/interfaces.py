from plone.app.layout.globals.interfaces import IViewView
from zope.interface import Attribute
from zope.interface import Interface
from zope.viewlet.interfaces import IViewlet as IBaseViewlet
from zope.viewlet.interfaces import IViewletManager


# Adapter

class IAdapter(Interface):
    """Base interface for adapters"""

    def catalog():  # pragma: no cover
        """Return portal_catalog"""

    def context_path():  # pragma: no cover
        """Path of the context"""

    def get_brains(interfaces=None, **query):  # pragma: no cover
        """Get brains."""

    def get_objects(interfaces=None, **query):  # pragma: no cover
        """Get objects."""

    def get_brain(interfaces=None, **query):  # pragma: no cover
        """Get brain which is supposed to be only one."""

    def get_object(interfaces=None, **query):  # pragma: no cover
        """Get object which is supposed to be only one."""

    def get_content_listing(interfaces=None, **query):  # pragma: no cover
        """Get ContentListing from brains gotten from get_brains method."""

    def getSessionData(create=True):  # pragma: no cover
        """getSessionData method from session_data_manager"""

    def event_datetime(item):  # pragma: no cover
        """Return ulocalized_time event datetime."""

    def portal():  # pragma: no cover
        """Portal object"""

    def portal_path():  # pragma: no cover
        """Path of the portal"""

    def membership():  # pragma: no cover
        """Return portal_membership"""


# View

class IBaseView(IViewView):
    """View interface for base view"""

    title = Attribute('Title of context')
    description = Attribute('Description of context')


class IBaseFormView(IBaseView):
    """View interface for base form"""


# Viewlet manager

class IBaseViewViewletManager(IViewletManager):
    """Viewlet manager interface for base view"""


class IBaseFormViewletManager(IViewletManager):
    """Viewlet manager interface for base form"""


class IRepeatedViewletManager(IViewletManager):
    """Viewlet manager interface for repeated viewlet"""

    def items():  # pragma: no cover
        """Return list

        :rtype: list
        """

    def render():  # pragma: no cover
        """Render viewletmanager

        :rtype: unicode
        """


# Viewlet

class IViewlet(IBaseViewlet):
    """Base viewlet interface to override method: render"""

    def render():  # pragma: no cover
        """Render viewlet

        :rtype: unicode
        """

    def repeated(item):  # pragma: no cover
        """Render viewlet with argument

        :rtype: unicode
        """

    def available():  # pragma: no cover
        """Return True or False

        :rtype: bool
        """
