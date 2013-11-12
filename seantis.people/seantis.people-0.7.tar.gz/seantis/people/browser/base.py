from five import grok
from plone.directives.form import Form
from z3c.form.interfaces import ActionExecutionError
from zope.interface import Invalid

from seantis.plonetools import tools
from seantis.people.interfaces import ISeantisPeopleSpecific


class BaseView(grok.View):

    grok.baseclass()
    grok.layer(ISeantisPeopleSpecific)

    def translate(self, text):
        return tools.translator(self.request, 'seantis.people')(text)


class BaseForm(Form):

    grok.baseclass()
    grok.layer(ISeantisPeopleSpecific)

    @property
    def parameters(self):
        data, errors = self.extractData()

        if errors:
            self.status = self.formErrorsMessage
            return None
        else:
            return data

    def raise_action_error(self, msg):
        raise ActionExecutionError(Invalid(msg))
