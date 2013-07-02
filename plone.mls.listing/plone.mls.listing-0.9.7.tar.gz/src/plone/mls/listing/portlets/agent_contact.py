# -*- coding: utf-8 -*-
"""Agent Contact Portlet."""

#python imports
from email import message_from_string
import re

# zope imports
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as PMF
from plone.app.portlets.portlets import base
from plone.directives import form
from plone.portlets.interfaces import IPortletDataProvider
from plone.z3cform import z2
from z3c.form import button, field, validator
from z3c.form.interfaces import HIDDEN_MODE, IFormLayer
from zope import formlib, schema
from zope.interface import Interface, Invalid, alsoProvides, implementer
from zope.schema.fieldproperty import FieldProperty

# local imports
from plone.mls.listing.browser.interfaces import IListingDetails
from plone.mls.listing.i18n import _

# starting from 0.6.0 version plone.z3cform has IWrappedForm interface
try:
    from plone.z3cform.interfaces import IWrappedForm
    HAS_WRAPPED_FORM = True
except ImportError:
    HAS_WRAPPED_FORM = False

from plone.formwidget.captcha.widget import CaptchaFieldWidget
from plone.formwidget.captcha.validator import CaptchaValidator

MSG_PORTLET_DESCRIPTION = _(
    u'This portlet shows a form to contact the corresponding agent for a '
    u'given listing via email.'
)

EMAIL_TEMPLATE = """\
Enquiry from: %(name)s <%(sender_from_address)s>
Listing URL: %(url)s

Message:
%(message)s
"""

EMAIL_TEMPLATE_RL = """\
Enquiry from: %(name)s <%(sender_from_address)s>
Listing URL: %(url)s

Phone Number: %(phone)s
Arrival Date: %(arrival_date)s
Departure Date: %(departure_date)s
Adults: %(adults)s
Children: %(children)s

Message:
%(message)s
"""

check_email = re.compile(
    r"[a-zA-Z0-9._%-]+@([a-zA-Z0-9-]+\.)*[a-zA-Z]{2,4}").match


def validate_email(value):
    if not check_email(value):
        raise Invalid(_(u'Invalid email address'))
    return True


class IEmailForm(Interface):
    """Email Form schema."""

    subject = schema.TextLine(
        required=False,
        title=PMF(u'label_subject', default=u'Subject')
    )

    name = schema.TextLine(
        description=PMF(
            u'help_sender_fullname',
            default=u'Please enter your full name',
        ),
        required=True,
        title=PMF(u'label_name', default=u"Name"),
    )

    sender_from_address = schema.TextLine(
        constraint=validate_email,
        description=PMF(
            u'help_sender_from_address',
            default=u'Please enter your e-mail address',
        ),
        required=True,
        title=PMF(u'label_sender_from_address', default=u'E-Mail'),
    )

    phone = schema.TextLine(
        missing_value=u'-',
        required=False,
        title=_(u'Phone Number'),
    )

    arrival_date = schema.TextLine(
        missing_value=u'-',
        required=False,
        title=_(u'Arrival Date'),
    )

    departure_date = schema.TextLine(
        missing_value=u'-',
        required=False,
        title=_(u'Departure Date'),
    )

    adults = schema.TextLine(
        missing_value=u'-',
        required=False,
        title=_(u'Adults'),
    )

    children = schema.TextLine(
        missing_value=u'-',
        required=False,
        title=_(u'Children'),
    )

    message = schema.Text(
        description=PMF(
            u'help_message',
            default=u'Please enter the message you want to send.',
        ),
        max_length=1000,
        required=True,
        title=PMF(u'label_message', default=u'Message'),
    )

    captcha = schema.TextLine(
        required=True,
        title=_(u'Captcha'),
    )


class EmailForm(form.Form):
    """Email Form."""
    fields = field.Fields(IEmailForm).omit(
        'phone', 'arrival_date', 'departure_date', 'adults', 'children',
    )
    ignoreContext = True
    method = 'post'
    _email_sent = False

    def __init__(self, context, request, portlet_hash=None, info=None,
                 data=None):
        super(EmailForm, self).__init__(context, request)
        self.listing_info = info
        self.data = data
        if portlet_hash:
            self.prefix = portlet_hash + '.' + self.prefix

    @property
    def already_sent(self):
        return self._email_sent

    @property
    def is_residential_lease(self):
        return self.listing_info.get('listing_id', '').lower().startswith('rl')

    def update(self):
        if self.is_residential_lease:
            self.fields = field.Fields(IEmailForm)
        self.fields['captcha'].widgetFactory = CaptchaFieldWidget
        super(EmailForm, self).update()

    def updateWidgets(self):
        super(EmailForm, self).updateWidgets()
        urltool = getToolByName(self.context, 'portal_url')
        portal = urltool.getPortalObject()
        subject = '%(portal_title)s: %(title)s (%(lid)s)' % dict(
            lid=self.listing_info['listing_id'],
            portal_title=portal.getProperty('title'),
            title=self.listing_info['listing_title'],
        )
        self.widgets['subject'].mode = HIDDEN_MODE
        self.widgets['subject'].value = subject

    @button.buttonAndHandler(PMF(u'label_send', default='Send'), name='send')
    def handle_send(self, action):
        """Send button for sending the email."""
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        if 'captcha' in data:
            # Verify the user input against the captcha
            captcha = CaptchaValidator(
                self.context, self.request, None, IEmailForm['captcha'], None,
            )
            if not self.already_sent and captcha.validate(data['captcha']):
                self.send_email(data)
                self._email_sent = True
        return

    def send_email(self, data):
        mailhost = getToolByName(self.context, 'MailHost')
        urltool = getToolByName(self.context, 'portal_url')
        portal = urltool.getPortalObject()
        email_charset = portal.getProperty('email_charset')

        # Construct and send a message.
        from_address = portal.getProperty('email_from_address')
        from_name = portal.getProperty('email_from_name')
        if from_name is not None:
            from_address = '%s <%s>' % (from_name, from_address)

        try:
            rcp = self.listing_info['agent'].get('agent_email').get('value')
        except:
            rcp = from_address

        sender = '%s <%s>' % (data['name'], data['sender_from_address'])
        subject = data['subject']
        data['url'] = self.request.getURL()
        if self.is_residential_lease:
            message = EMAIL_TEMPLATE_RL % data
        else:
            message = EMAIL_TEMPLATE % data
        message = message_from_string(message.encode(email_charset))
        message['To'] = rcp
        message['From'] = from_address
        message['Cc'] = sender
        if getattr(self.data, 'bcc', None) is not None:
            message['Bcc'] = self.data.bcc
        message['Reply-to'] = sender
        message['Subject'] = subject

        mailhost.send(message, immediate=True, charset=email_charset)
        return

# Register Captcha validator for the captcha field in the ICaptchaForm
validator.WidgetValidatorDiscriminators(CaptchaValidator, field=IEmailForm['captcha'])


class IAgentContactPortlet(IPortletDataProvider):
    """A portlet which sends an email to the agent."""

    heading = schema.TextLine(
        description=_(
            u'Custom title for the portlet. If no title is provided, the '
            u'default title is used.'
        ),
        required=False,
        title=_(u'Portlet Title'),
    )

    description = schema.Text(
        description=_(u'Additional description for the portlet.'),
        required=False,
        title=_('Description'),
    )

    mail_sent_msg = schema.Text(
        description=_(
            u'Thank you message that is shown after the mail was sent.'
        ),
        required=False,
        title=_(u'Mail Sent Message'),
    )

    bcc = schema.TextLine(
        description=_(
            u'E-mail addresses which receive a blind carbon copy (comma '
            u'separated).'
        ),
        required=False,
        title=_(u'BCC Recipients'),
    )


@implementer(IAgentContactPortlet)
class Assignment(base.Assignment):
    """Agent Contact Portlet Assignment."""

    heading = FieldProperty(IAgentContactPortlet['heading'])
    description = FieldProperty(IAgentContactPortlet['description'])
    mail_sent_msg = FieldProperty(IAgentContactPortlet['mail_sent_msg'])
    bcc = FieldProperty(IAgentContactPortlet['bcc'])
    title = _(u'Agent Contact')

    def __init__(self, heading=None, description=None, mail_sent_msg=None,
                 bcc=None):
        self.heading = heading
        self.description = description
        self.mail_sent_msg = mail_sent_msg
        self.bcc = bcc


class Renderer(base.Renderer):
    """Agent Information Portlet Renderer."""

    @property
    def already_sent(self):
        return self.form.already_sent

    @property
    def available(self):
        return IListingDetails.providedBy(self.view) and \
            getattr(self.view, 'listing_id', None) is not None

    @property
    def description(self):
        return self.data.description

    @property
    def mail_sent_msg(self):
        return self.data.mail_sent_msg or PMF(u"Mail sent.")

    @property
    def title(self):
        return self.data.heading or self.data.title

    def update(self):
        if self.view.info is None:
            return
        listing_info = {
            'listing_id': self.view.info.get('id').get('value'),
            'listing_title': self.view.info.get('title').get('value'),
            'agent': self.view.contact.get('agent'),
        }

        z2.switch_on(self, request_layer=IFormLayer)
        portlet_hash = self.__portlet_metadata__.get('hash')
        self.form = EmailForm(aq_inner(self.context), self.request,
                              portlet_hash, listing_info, self.data)
        if HAS_WRAPPED_FORM:
            alsoProvides(self.form, IWrappedForm)
        self.form.update()


class AddForm(base.AddForm):
    """Add form for the Agent Contact portlet."""
    form_fields = formlib.form.Fields(IAgentContactPortlet)
    label = _(u'Add Agent Information portlet')
    description = MSG_PORTLET_DESCRIPTION

    def create(self, data):
        assignment = Assignment()
        formlib.form.applyChanges(assignment, self.form_fields, data)
        return assignment


class EditForm(base.EditForm):
    """Edit form for the Agent Contact portlet"""
    form_fields = formlib.form.Fields(IAgentContactPortlet)
    label = _(u'Edit Agent Information portlet')
    description = MSG_PORTLET_DESCRIPTION
