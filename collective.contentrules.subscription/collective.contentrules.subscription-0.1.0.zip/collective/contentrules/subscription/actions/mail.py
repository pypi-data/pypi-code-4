# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from collective.contentrules.subscription import logger
from collective.contentrules.subscription import subscriptionMessageFactory as _
from OFS.SimpleItem import SimpleItem
from plone.app.contentrules.browser.formhelper import AddForm, EditForm
from plone.contentrules.rule.interfaces import IRuleElementData, IExecutable
from plone.stringinterp.interfaces import IStringInterpolator
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _plone
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.MailHost.MailHost import MailHostError
from smtplib import SMTPException
from zope import schema
from zope.app.component.hooks import getSite
from zope.component import adapts
from zope.component.interfaces import ComponentLookupError
from zope.formlib import form
from zope.interface import Interface, implements
import traceback
import uuid


class IMailSubscriptionsAction(Interface):
    """Definition of the configuration available for a mail action
    """
    subject = schema.TextLine(
        title=_plone(u"Subject"),
        description=_plone(u"Subject of the message"),
        required=True)
    source = schema.TextLine(
        title=_plone(u"Email source"),
        description=_plone("The email address that sends the \
email. If no email is provided here, it will use the portal from address."),
        required=False)
    message = schema.Text(title=_(u"Message"),
                          description=_(u"The message that you want to mail."),
                          required=True)


class MailSubscriptionsAction(SimpleItem):
    """
    The implementation of the action defined before
    """
    implements(IMailSubscriptionsAction, IRuleElementData)

    subject = u''
    source = u''
    message = u''
    element = 'plone.actions.MailSubscriptions'

    def __init__(self):
        super(MailSubscriptionsAction, self).__init__()
        self.actionUID = self.generateActionUID()

    def generateActionUID(self):
        """
        Actions doesn't have an unique id, so we generate one
        """
        #BBB there is a better way to do this?
        site = getSite()
        rules_tool = getToolByName(site, 'contentrules_subscription_tool')
        action_uuid = uuid.uuid4()
        if str(action_uuid) in rules_tool.getActionUIDS():
            action_uuid = uuid.uuid4()
        return str(action_uuid)

    @property
    def summary(self):
        return _(u"Email report to users subscribed")


class MailActionExecutor(object):
    """The executor for this action.
    """
    implements(IExecutable)
    adapts(Interface, IMailSubscriptionsAction, Interface)

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        mailhost = getToolByName(aq_inner(self.context), "MailHost")

        if not mailhost:
            raise ComponentLookupError(
                'You must have a Mailhost utility to execute this action')

        source = self.element.source
        urltool = getToolByName(aq_inner(self.context), "portal_url")
        portal = urltool.getPortalObject()
        email_charset = portal.getProperty('email_charset')
        if not source:
            # no source provided, looking for the site wide from email
            # address
            from_address = portal.getProperty('email_from_address')
            if not from_address:
                raise ValueError("You must provide a source address for this \
action or enter an email in the portal properties")
            from_name = portal.getProperty('email_from_name').strip('"')
            source = '"%s" <%s>' % (from_name, from_address)

        obj = self.event.object

        interpolator = IStringInterpolator(obj)
        rules_tool = getToolByName(aq_inner(self.context), 'contentrules_subscription_tool')
        recipients_mail = rules_tool.getRegisteredList(self.element.actionUID)

        # Prepend interpolated message with \n to avoid interpretation
        # of first line as header.
        message = "\n%s" % interpolator(self.element.message)
        subject = interpolator(self.element.subject)
        logger.info("Sending mail to recipients: %s" % ", ".join(recipients_mail))
        for recipient in recipients_mail:
            try:
                # XXX: We're using "immediate=True" because otherwise we won't
                # be able to catch SMTPException as the smtp connection is made
                # as part of the transaction apparatus.
                # AlecM thinks this wouldn't be a problem if mail queuing was
                # always on -- but it isn't. (stevem)
                # so we test if queue is not on to set immediate
                mailhost.send(message, recipient, source,
                              subject=subject, charset=email_charset,
                              immediate=not mailhost.smtp_queue)
            except (MailHostError, SMTPException):
                logger.error(
                    """mailing error: Attempt to send mail in content rule failed.\n%s""" %
                    traceback.format_exc())
        return True


class MailSubscriptionsAddForm(AddForm):
    """
    An add form for the mail action
    """
    form_fields = form.FormFields(IMailSubscriptionsAction)
    label = _plone(u"Add Mail Action")
    description = _(u'form_description',
        default=u"A mail action that can mail users subscribed to this rule")
    form_name = _plone(u"Configure element")

    # custom template will allow us to add help text
    template = ViewPageTemplateFile('templates/mail.pt')

    def create(self, data):
        a = MailSubscriptionsAction()
        form.applyChanges(a, self.form_fields, data)
        return a


class MailSubscriptionsEditForm(EditForm):
    """
    An edit form for the mail action
    """
    form_fields = form.FormFields(IMailSubscriptionsAction)
    label = _plone(u"Edit Mail Subscriptions Action")
    description = _(u'form_description',
        default=u"A mail action that can mail users subscribed to this rule")
    form_name = _plone(u"Configure element")

    # custom template will allow us to add help text
    template = ViewPageTemplateFile('templates/mail.pt')
