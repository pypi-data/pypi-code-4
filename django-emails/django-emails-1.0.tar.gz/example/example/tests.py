# coding: utf-8
from django.test import TestCase
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_unicode

from emails.engine import MailSender
from emails.models import Message, Recipient

from models import Example
from emails.signals import send_notification

class SimpleTest(TestCase):
    mail_sender = MailSender()
    
    def test_send_textmail(self):
        self.mail_sender.send_mail('Test text mail subject 1', settings.TEST_EMAIL_ADDRESS, 'Test text mail content 1')
        message = Message.objects.get(subject = 'Test text mail subject 1', content = 'Test text mail content 1', 
                                      priority = 2, type = 'plain')
        
        self.assertTrue(message, 'Message exists')
        self.assertEqual(Recipient.objects.filter(message = message, address = settings.TEST_EMAIL_ADDRESS).count(),
                         1, 'Only one recipient')
        
    def test_send_textmails(self):
        self.mail_sender.send_mails('Test text mail subject 2', 
                                    [settings.TEST_EMAIL_ADDRESS, settings.TEST_EMAIL_ADDRESS], 
                                    'Test text mail content 2')
        message = Message.objects.get(subject = 'Test text mail subject 2', 
                                      content = 'Test text mail content 2', 
                                      priority = 2, type = 'plain')
        self.assertTrue(message, 'Message exists')
        self.assertEqual(Recipient.objects.filter(message = message, address = settings.TEST_EMAIL_ADDRESS).count(),
                         2, 'Two recipients')
        
        
    def test_send_htmlmail(self):
        self.mail_sender.send_mail('Test text mail subject 3', settings.TEST_EMAIL_ADDRESS, 
                                   '<strong>Test text mail content</strong>', type='html', priority = 1)
        self.assertTrue(Message.objects.get(subject = 'Test text mail subject 3', 
                                            content = '<strong>Test text mail content</strong>', 
                                            priority = 1, type = 'html'), 
                        'Message exists')
    
    def test_send_templatemail(self):
        template = 'emails/test.html'
        context = {'text': 'test template mail content'}
        self.mail_sender.send_htmlmail('Test template mail subject', settings.TEST_EMAIL_ADDRESS, template, 
                                       context, 3)
        message = Message.objects.get(subject = 'Test template mail subject', 
                                      content = render_to_string(template, context), 
                                      priority = 3, type = 'html')
        self.assertTrue(message, 'Message exists')
        
    
    def test_signals(self):
        user = User.objects.create(password='', username='test_user', is_active=True, is_staff=True, 
                                   email = settings.TEST_EMAIL_ADDRESS)
        content_type = ContentType.objects.get_for_model(Example)
        codename = send_notification.perm_name % content_type.model
        permission, created = Permission.objects.get_or_create(content_type=content_type, codename=codename)
        user.user_permissions.add(permission)

        Example.objects.create(email = settings.TEST_EMAIL_ADDRESS, text = 'test signals', boolean = True)
        
        notification_message = Message.objects.get(subject = force_unicode(_('It was created a new item')), 
                                                   priority = 2, type = 'html')
        
        self.assertTrue(notification_message, 'Notification message exists')
        
        field_notification_message = Message.objects.get(subject = 'Test field notification', 
                                                         priority = 2, type = 'html')
        self.assertTrue(field_notification_message, 'Notification message exists')
        
        
    def tearDown(self):
        if settings.TEST_EMAIL_ADDRESS != 'test@test.cz':
            print self.mail_sender.send_batch()