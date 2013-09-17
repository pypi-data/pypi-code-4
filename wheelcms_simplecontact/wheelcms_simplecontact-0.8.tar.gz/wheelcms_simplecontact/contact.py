from smtplib import SMTPException

from django.conf import settings
from django import forms
from django.shortcuts import render_to_response
from django.core.mail import send_mail

from stracks_api.client import exception, error
from two.ol.util import get_client_ip

from wheelcms_axle.actions import action_registry
from wheelcms_axle.models import Configuration

class ContactForm(forms.Form):
    sender = forms.EmailField(
                  help_text="The email address you can be reached on")
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)

##    TODO:
##    - include authenticated data, if any. Optionally do not require sender
##
def contact_handler(handler, request, action):
    handler.context['form'] = ContactForm()
    if handler.post:
        handler.context['form'] = form = ContactForm(request.POST)
        if form.is_valid():
            sender = form.cleaned_data.get('sender', '')
            title = handler.instance.content().title
            message = form.cleaned_data.get('message', '')
            receiver = Configuration.config().mailto
            ip = get_client_ip(request)

            if not receiver:
                try:
                    receiver = settings.ADMINS[0][1]
                except IndexError:
                    error("No suitable receiver for contactform found",
                          data=dict(sender=sender, title=title, message=message))
                    return handler.redirect(handler.instance.path or '/',
                                    error="Unfortunately, something went wrong")


            body = """\
Message from %(sender)s @ %(ip)s

==

%(message)s
""" % dict(sender=sender, ip=ip, message=message)

            try:
                send_mail('Feedback from %s on "%s"' % (sender, title),
                          body,
                          sender,
                          [receiver],
                          fail_silently=False
                          )
            except (SMTPException, Exception):
                exception("failed to send form",
                          data=dict(sender=sender, title=title, message=message))
                return handler.redirect(handler.instance.path or '/',
                                        error="Unfortunately, something went wrong")

            ### Handle smtp issues! fail_silently=False
            return handler.redirect(handler.instance.path or '/',
                                    success="Your feedback has been sent")
    return render_to_response("wheelcms_simplecontact/contact.html",
                              handler.context)

action_registry.register(contact_handler, "contact")
