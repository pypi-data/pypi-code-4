# -*- coding: utf-8 -*-
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy
from django.core.mail.message import EmailMultiAlternatives
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.views.generic import FormView

from .forms import ContactForm
from .settings import (
    CONTACT_FORM_RULES,
    CONTACT_FORM_ALLOW_DIRECT_USER_CONTACT as ALLOW_DIRECT
)


class ContactFormView(FormView):
    form_class = ContactForm
    success_url = reverse_lazy('home')
    template_name = 'contact/form.html'

    def __init__(self, **kwargs):
        """
        Add the user attribute to the class
        """
        self.recipient = None
        self.subject = 'default'
        self.allow_direct = ALLOW_DIRECT
        super(ContactFormView, self).__init__(**kwargs)

    def _get_rule(self, name):
        """
        Get CONTACT_FORM_RULES rule by its name
        """
        return CONTACT_FORM_RULES.get(name, None)

    def dispatch(self, request, *args, **kwargs):
        """
        Get the recipient or subject object given the contact url
        """
        if self.allow_direct:
            slug = kwargs.get('slug', None)
            if slug:
                User = get_user_model()
                self.recipient = get_object_or_404(User, slug=slug)

            pk = kwargs.get('pk', None)
            if pk:
                User = get_user_model()
                self.recipient = get_object_or_404(User, pk=pk)

        subject = kwargs.get('subject', None)
        if subject:
            self.subject = subject

        return super(ContactFormView, self).dispatch(request, *args, **kwargs)

    def get_form(self, form_class):
        """
        Set the recipient_id field value
        """
        form = super(ContactFormView, self).get_form(form_class)
        if self.allow_direct and self.recipient:
            form.fields['recipient_id'].initial = self.recipient.id
        if self.subject:
            form.fields['subject'].initial = self.subject
        return form

    def get_context_data(self, **kwargs):
        """
        Add the recipient user object to the context (useful to add contact
        informations to the form template).
        """
        ctx = super(ContactFormView, self).get_context_data(**kwargs)
        if self.allow_direct and self.recipient:
            ctx.update({'recipient': self.recipient})
        return ctx

    def format_subject(self):
        """
        Format the email subject
        """
        rule = self._get_rule(self.subject)
        prefix = rule['prefix']
        subject = rule['subject']
        return '%s %s' % (prefix, subject)

    def send_email(self, form):
        """
        Sends a message to the CONTACT_FORM_RECIPIENT_LIST or to MANAGERS if
        not set in settings file.
        """
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        sender = form.cleaned_data['sender']
        recipient_id = form.cleaned_data['recipient_id']
        rule_name = form.cleaned_data['subject']
        message = form.cleaned_data['message']

        # Get subject for submitted rule
        rule = self._get_rule(rule_name)
        formated_subject = self.format_subject()

        # Recipent
        if self.allow_direct and recipient_id:
            User = get_user_model()
            recipient = get_object_or_404(User, id=recipient_id)
            to = (recipient.email, )
        else:
            to = rule['to']

        # Sender
        full_name = "%s %s" % (first_name, last_name)
        if len(full_name) > 1:
            sender = "%s <%s>" % (full_name, sender)

        # Email object
        mail = EmailMultiAlternatives(formated_subject,
                                      message, sender, to)
        try:
            mail.send(fail_silently=False)
            msg = _("Thank you for your feedback.")
            messages.add_message(self.request, messages.SUCCESS, msg)
        except:
            msg = _("An error occured while trying to send contact email.")
            # FIXME
            # Log the message here
            messages.add_message(self.request, messages.ERROR, msg)

    def form_valid(self, form):
        """
        When the form is valid, send an email!
        """
        self.send_email(form)
        return super(ContactFormView, self).form_valid(form)
