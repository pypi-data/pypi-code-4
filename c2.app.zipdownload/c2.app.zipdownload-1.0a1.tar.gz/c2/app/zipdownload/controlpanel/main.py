

from Acquisition import aq_inner
from plone.app.registry.browser import controlpanel
from zope.component import getMultiAdapter
from Products.Five.browser import BrowserView
from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from c2.app.zipdownload.controlpanel.interfaces import IZipDownloadControlPanel
from c2.app.zipdownload import ZipDownloadMessageFactory as _


class ZipDownloadEditForm(controlpanel.RegistryEditForm):

    schema = IZipDownloadControlPanel
    label = _(u"Zip Download settings")


class ZipDownloadControlPanel(controlpanel.ControlPanelFormWrapper):
    form = ZipDownloadEditForm


