from zope import interface, schema
from z3c.form import form, field, button, validator
from plone.z3cform.layout import wrap_form
from collective.contentrules.subscription import subscriptionMessageFactory as _
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from collective.z3cform.norobots.widget import NorobotsFieldWidget
from collective.z3cform.norobots.validator import NorobotsValidator
from zope.component import provideAdapter
import re


class IsEmailError(schema.ValidationError):
    __doc__ = _("""You entered an invalid email address.""")


def isEmail(value):
    expr = re.compile(r"^(\w&.%#$&'\*+-/=?^_`{}|~]+!)*[\w&.%#$&'\*+-/=?^_`{}|~]+@(([0-9a-z]([0-9a-z-]*[0-9a-z])?\.)+[a-z]{2,6}|([0-9]{1,3}\.){3}[0-9]{1,3})$", re.IGNORECASE)
    if expr.match(value):
        return True
    raise IsEmailError


class IContentruleSubscription(interface.Interface):
    email = schema.TextLine(title=_(u"Email"),
                            constraint=isEmail,
                            required=True)

    rules = schema.Tuple(
            title=_(u'Available notifications'),
            description=_(u"These are the available notifications which you can subscribe for."),
            value_type=schema.Choice(vocabulary=u"contentrules.subscription.vocabularies.SubscriptionRulesVocabulary"),
            required=True,
            missing_value=()
        )
    norobots = schema.TextLine(title=_(u'Are you a human ?'),
                               description=_(u'In order to avoid spam, please answer the question below.'),
                               required=True)


class ContentruleSubscriptionForm(form.Form):
    fields = field.Fields(IContentruleSubscription)
    fields['rules'].widgetFactory = CheckBoxFieldWidget
    fields['norobots'].widgetFactory = NorobotsFieldWidget
    ignoreContext = True # don't use context to get widget data
    label = _("Subscribe to site notifications")
    description = _("In this form you can choose which notifications subscribe for.")

    def updateWidgets(self):
        super(ContentruleSubscriptionForm, self).updateWidgets()
        pm = getToolByName(self.context, 'portal_membership')
        user_email = pm.getAuthenticatedMember().getProperty('email')
        if user_email:
            self.widgets["email"].value = user_email

    @button.buttonAndHandler(_(u'Subscribe'))
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            return
        rules_tool = getToolByName(self.context, 'contentrules_subscription_tool')
        errors = []
        for rule in data.get('rules'):
            result, msg = rules_tool.registerUser(rule, data.get('email', ''))
            if not result:
                IStatusMessage(self.request).addStatusMessage(msg, "error")
            else:
                IStatusMessage(self.request).addStatusMessage(_(u"You are subscribed succesfully."),
                                                      "info")
        self.context.REQUEST.RESPONSE.redirect("@@notify-subscribe")

ContentruleSubscriptionView = wrap_form(ContentruleSubscriptionForm)

# Register Norobots validator for the correponding field in the IContactInfo interface
validator.WidgetValidatorDiscriminators(NorobotsValidator, field=IContentruleSubscription['norobots'])

# Register the validator so it will be looked up by z3c.form machinery

provideAdapter(NorobotsValidator)
