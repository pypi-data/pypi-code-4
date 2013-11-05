# -*- coding: utf-8 -*-
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import mock

from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.auth.models import User
from django.core import mail
from django.core.urlresolvers import reverse_lazy
from django.test import RequestFactory, TestCase

from .views import ContactFormView
from .settings import CONTACT_FORM_RULES


class ContactFormViewTest(TestCase):
    urls = 'td_contact.test_urls'

    def setUp(self):
        # Class based view to test
        self.view_class = ContactFormView

        # Create a test user
        self.user = User.objects.create_user(
            'johndoe',
            email='john@doe.com',
            password='anonymous42',
            first_name='John',
            last_name='Doe',
        )

        # The custom rule
        self.custom_rule = 'custom'

        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.valid_data = {
            'first_name': "John",
            'last_name': "Doe",
            'sender': "john@doe.com",
            'recipient_id': '',
            'subject': 'default',
            'message': 'This is my message',
        }

    def _setup_view(self, view, request, *args, **kwargs):
        """
        Mimic as_view() returned callable, but returns view instance.
        args and kwargs are the same you would pass to ``reverse()``

        Source: http://tech.novapost.fr/django-unit-test-your-views-en.html
        """
        view.request = request
        view.args = args
        view.kwargs = kwargs
        return view

    def _get_view(self, request, *args, **kwargs):
        """
        Get the class based view instance
        """
        view = self.view_class()
        return self._setup_view(view, request, *args, **kwargs)

    def _patch_messages(self, request):
        """
        Ugly patch found at:
        http://stackoverflow.com/a/12011907
        """
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        return request

    def _get_rule_view(self, rule, **kwargs):
        """
        Get a particular rule view
        """
        url = reverse_lazy('contact_form_rule', kwargs={'subject': rule})
        request = self.factory.get(url)
        request = self._patch_messages(request)
        view = self._get_view(request, None, subject=rule)
        return view

    # Unit tests
    def test_dispatch(self):
        """
        Test class_view dispatch method
        """
        view = self._get_rule_view(self.custom_rule)
        response = view.dispatch(view.request, *view.args, **view.kwargs)

        self.assertEqual(view.subject, self.custom_rule)
        self.assertEqual(response.status_code, 200)

    def test_get_form(self):
        """
        Test class_view get_form method
        """
        view = self._get_rule_view(self.custom_rule)
        form = view.get_form(view.form_class)

        self.assertEqual(form.fields['subject'].initial, view.subject)

    def test_get_context_data(self):
        """
        Test class_view get_context_data method
        """
        view = self._get_rule_view(self.custom_rule)
        view.recipient = self.user
        context = view.get_context_data()

        self.assertIn('recipient', context)
        self.assertEqual(context['recipient'], self.user)

    def test_format_subject(self):
        """
        Test class_view format_subject method
        """
        view = self._get_rule_view(self.custom_rule)
        rule = view._get_rule(self.custom_rule)
        view.subject = self.custom_rule
        subject = view.format_subject()

        self.assertEqual(subject, "%(prefix)s %(subject)s" % rule)

    def test_send_email(self):
        """
        Test class_view send_email method
        """
        view = self._get_rule_view(self.custom_rule)

        # Get the filled form
        form_class = view.get_form_class()
        form = form_class(data=self.valid_data)
        form.is_valid()

        # Send this email
        view.send_email(form)

        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)

    @mock.patch('django.core.mail.message.EmailMultiAlternatives.send',
                mock.Mock(side_effect=Exception('Boom!')))
    def test_send_email_failure(self):
        """
        Test class_view send_email method mocked with a django send_mail
        failure
        """
        view = self._get_rule_view(self.custom_rule)

        # Get the filled form
        form_class = view.get_form_class()
        form = form_class(data=self.valid_data)
        form.is_valid()

        # Send this email
        view.send_email(form)

        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 0)

    def test_form_valid(self):
        """
        Tests class_view form_valid method

        At this time this is more or less the same test as test_send_email
        """
        view = self._get_rule_view(self.custom_rule)

        # Get the filled form
        form_class = view.get_form_class()
        form = form_class(data=self.valid_data)
        form.is_valid()

        # Valid the form (and send email)
        view.form_valid(form)

        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)

    # Functional tests
    def test_get_default_rule(self):
        """
        Tests the default rule view with the test client
        """
        url = reverse_lazy('contact_form')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context_data)

    def test_get_custom_rule(self):
        """
        Tests the default rule view with the test client
        """
        rule = 'custom'
        url = reverse_lazy('contact_form_rule', kwargs={'subject': rule})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context_data)

        form = response.context_data['form']
        subject_initial = form.fields['subject'].initial
        self.assertEqual(subject_initial, rule)

    def test_get_user_id(self):
        """
        Tests the default rule view with the test client
        """
        url = reverse_lazy('user_contact_form_by_pk',
                           kwargs={'pk': self.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context_data)
        self.assertTrue('recipient' in response.context_data)

        recipient = response.context_data['recipient']
        self.assertEqual(recipient, self.user)

    def test_post_default_rule(self):
        """
        Test data submission for the default rule with the test client
        """
        url = reverse_lazy('contact_form')
        response = self.client.post(url, self.valid_data)

        # We must redirect on success
        self.assertEqual(response.status_code, 302)

        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)

    def test_post_custom_rule(self):
        """
        Test data submission for the default rule with the test client
        """
        rule = 'custom'
        url = reverse_lazy('contact_form_rule', kwargs={'subject': rule})
        response = self.client.post(url, self.valid_data)

        # We must redirect on success
        self.assertEqual(response.status_code, 302)

        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)

        # Verify that the subject of the first message is correct.
        subject = "%(prefix)s %(subject)s" % CONTACT_FORM_RULES[rule]
        self.assertEqual(mail.outbox[0].subject, subject)

    def test_post_custom_rule_redirect(self):
        """
        Test data submission for the default rule with the test client
        """
        url = reverse_lazy(u'contact_form')
        response = self.client.post(url, self.valid_data, follow=True)

        # We have redirected on success
        self.assertEqual(response.status_code, 200)

        # Test that a message has been added
        self.assertTrue('messages' in response.context)

        # Get the latest message
        messages = response.context['messages']
        self.assertEqual(len(messages), 1)

        # Test this success message
        message = [m for m in messages][0]
        self.assertEqual(message.tags, 'success')
        self.assertTrue("Thank you for your feedback." in message.message)

    def test_post_user_id(self):
        """
        Tests the default rule view with the test client
        """
        url = reverse_lazy('user_contact_form_by_pk',
                           kwargs={'pk': self.user.id})
        self.valid_data.update({
            'recipient_id': self.user.id
        })
        response = self.client.post(url, self.valid_data)

        # We must redirect on success
        self.assertEqual(response.status_code, 302)

        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)

        # Our user must be the recipient
        mailto = mail.outbox[0].to[0]
        self.assertEqual(mailto, self.user.email)
