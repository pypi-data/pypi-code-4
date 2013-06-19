from urlparse import urlparse
from Acquisition import aq_inner
from plone.app.registry.browser import controlpanel
from zope.component import getMultiAdapter
from Products.Five.browser import BrowserView
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from fourdigits.portlet.twitter.controlpanel.interfaces import \
            IFourdigitPortletTwitterSetting
from fourdigits.portlet.twitter import \
            FourdigitsPortletTwitterMessageFactory as _



class FourdigitPortletTwitterSettingEditForm(controlpanel.RegistryEditForm):

    schema = IFourdigitPortletTwitterSetting
    label = _(u"Twitter Portlet Settings")


class FourdigitPortletTwitterSettingControlPanel(controlpanel.ControlPanelFormWrapper):
    form = FourdigitPortletTwitterSettingEditForm

