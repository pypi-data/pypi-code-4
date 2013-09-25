from five import grok

from plone import api
from plone.app.textfield.value import RichTextValue

from collective.local.sendto.interfaces import IMailSentEvent


@grok.subscribe(IMailSentEvent)
def mail_sent(event):
    sent_mails_folder = api.portal.get()['sent-mails']
    recipients = [recipient.getId() for recipient in event.recipients]
    api.content.create(type='sent_mail',
                       title=event.subject,
                       body=RichTextValue(raw=event.body,
                                          mimeType="text/html",
                                          outputMimeType="text/x-html-safe",
                                          encoding='utf-8'),
                       recipients=recipients,
                       container=sent_mails_folder)
