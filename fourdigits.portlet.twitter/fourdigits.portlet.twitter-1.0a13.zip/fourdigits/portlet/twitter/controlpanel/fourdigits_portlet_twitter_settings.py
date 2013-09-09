from plone.app.registry.browser import controlpanel
from fourdigits.portlet.twitter.controlpanel.interfaces import \
            IFourdigitPortletTwitterSetting
from fourdigits.portlet.twitter import \
            FourdigitsPortletTwitterMessageFactory as _


class FourdigitPortletTwitterSettingEditForm(controlpanel.RegistryEditForm):

    schema = IFourdigitPortletTwitterSetting
    label = _(u"Twitter Portlet Settings")


class FourdigitPortletTwitterSettingControlPanel(controlpanel.ControlPanelFormWrapper):
    form = FourdigitPortletTwitterSettingEditForm
