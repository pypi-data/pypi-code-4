from zope.formlib import form
from plone.fieldsets.fieldsets import FormFieldsets

from zope.component import adapts
from zope.interface import implements
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode

from plone.app.controlpanel.form import ControlPanelForm
from zope.app.form.browser import MultiSelectWidget
from zope.app.form.browser import DisplayWidget

from zettwerk.clickmap import clickmapMessageFactory as _
from zettwerk.clickmap.interfaces import IClickmap, IClickmapSettings, IClickmapOutput

class ClickmapControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(IClickmap)

    def __init__(self, context):
        super(ClickmapControlPanelAdapter, self).__init__(context)
        self.portal = context
        clickmap_tool = getToolByName(self.portal, 'portal_clickmap')
        self.context = clickmap_tool

    output = ProxyFieldProperty(IClickmap['output'])
    setup = ProxyFieldProperty(IClickmap['setup'])
    reset = ProxyFieldProperty(IClickmap['reset'])
    enabled = ProxyFieldProperty(IClickmap['enabled'])
    pages = ProxyFieldProperty(IClickmap['pages'])
    output_width = ProxyFieldProperty(IClickmap['output_width'])
    right_align_threshold = ProxyFieldProperty(IClickmap['right_align_threshold'])
    output_height = ProxyFieldProperty(IClickmap['output_height'])


    def get_output_data(self):
        """ read the log data from the tool and prepare for output """

        logger = self.context.logger
        if logger is None:
            return []
        
        uids = logger.keys()
        catalog = getToolByName(self.portal, 'portal_catalog')

        returner = []
        for uid in uids:
            uid_log = logger.get(uid)
            brains = catalog(UID=uid)

            ## check for old log data 
            if not brains: 
                self.context._remove_uid_from_log(uid)
                continue

            brain = brains[0] ## uid is unique
            returner.append({
                'url': brain.getURL(),
                'title': brain['Title'],
                'clicks': len(uid_log)
                })

        return returner
    
class ListPagesMultiSelectWidget(MultiSelectWidget):
    def __init__(self, field, request):
        super(ListPagesMultiSelectWidget, self).__init__(
            field, field.value_type.vocabulary, request
            )

class JSSetupWidget(DisplayWidget):
    """ integrate some js functionality, to setup the clickmap settings  """

    def __call__(self):
        setup_description = u"""This tries to check, if your layout uses a variable or a fixed width.
                                Using a variable width, the current display witdh will be used as
                                reference. Then you should also check the right-align threshold."""
        return u'<a href="javascript:clickmapSetup()">%s</a><br />' \
               u'<div class="formHelp">%s</div>' %(_(u"Click here for automatical setup"),
                                                   _(setup_description))

class ResetWidget(DisplayWidget):
    """ a link to call the reset routine of the tool """

    def __call__(self):
        return '<a href="javascript:confirmClickmapReset()">Click here</a> if you want to reset your already logged clicks.'


class OutputWidget(DisplayWidget):
    """ list the logged pages as links to view the clickmap output """

    def __call__(self):
        adapter = self.context.context

        returner = []
        returner.append(u'<div class="formHelp">%s</div>' %(_("This list containes all available log data.")))

        returner.append(u'<ul>')
        for page in adapter.get_output_data():
            returner.append(safe_unicode('<li><strong>%(title)s</strong>: view <a target="_blank" href="%(url)s?show_clickmap_output=true">authenticated</a> or view <a target="_blank" href="%(url)s/clickmap_anonym_view">anonymous</a> (Clicks: %(clicks)s)' %(page)))
        returner.append(u'</ul>')
        
        return u'\n'.join(returner)

settings = FormFieldsets(IClickmapSettings)
settings.id = 'settings'
settings.label = _(u'Settings')

output = FormFieldsets(IClickmapOutput)
output.id = 'output'
output.label = _(u'Output')

class ClickmapControlPanel(ControlPanelForm):

    form_fields = FormFieldsets(settings, output)
    form_fields['pages'].custom_widget = ListPagesMultiSelectWidget

    form_fields['setup'].custom_widget = JSSetupWidget
    form_fields['setup'].for_display = True

    form_fields['reset'].custom_widget = ResetWidget
    form_fields['reset'].for_display = True

    form_fields['output'].custom_widget = OutputWidget
    form_fields['output'].for_display = True

    label = _(u"Zettwerk Clickmap")
    description = _(u'Important: by changing the width, height or threshold settings, already logged clicks might be not suitable any more. You should then reset the log.')
