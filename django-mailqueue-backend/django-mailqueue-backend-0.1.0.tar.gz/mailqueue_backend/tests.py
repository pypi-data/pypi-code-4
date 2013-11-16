import sys
import cStringIO
import traceback
from django.test import TestCase
from django.test.utils import override_settings
from django.test.client import Client
from django import http
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management import call_command
from queues import queues

def capture(func, *args, **kwargs):
    """Capture the output of func when called with the given arguments.

    The function output includes any exception raised. capture returns
    a tuple of (function result, standard output, standard error).
    """
    stdout, stderr = sys.stdout, sys.stderr
    sys.stdout = c1 = cStringIO.StringIO()
    sys.stderr = c2 = cStringIO.StringIO()
    result = None
    try:
        result = func(*args, **kwargs)
    except:# pragma: no cover
        traceback.print_exc()
    sys.stdout = stdout
    sys.stderr = stderr
    return (result, c1.getvalue(), c2.getvalue())

subject, from_email, to = 'hello', 'from@example.com', 'to@example.com'
text_content = 'This is an important message.'
html_content = '<p>This is an <strong>important</strong> message.</p>'
QUEUE_NAME = 'TEST_QUEUE'
EMAIL_BACKEND = "mailqueue_backend.mail.smtp.QueuedEmailBackend"

@override_settings(MAIL_QUEUE_NAME=QUEUE_NAME,EMAIL_BACKEND=EMAIL_BACKEND)
class SendMailTest(TestCase):
    def setUp(self):
        self.q = queues.Queue(QUEUE_NAME)

    def send_message(self):
        msg = EmailMultiAlternatives(subject, text_content,
            from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    @override_settings(EMAIL_HOST='',MAIL_QUEUE_EXPIRE=86400)
    def test_re_queue(self):
        ''' message will be requeued after fail '''
        self.send_message()
        self.assertEqual(len(self.q),1)
        capture(call_command,'process_mail_queue','test')
        self.assertEqual(len(self.q),1)
        self.q.read()

    @override_settings(EMAIL_HOST='',MAIL_QUEUE_EXPIRE=0)
    def test_de_queue(self):
        ''' message will expire and be dequeued '''
        self.send_message()
        self.assertEqual(len(self.q),1)
        capture(call_command,'process_mail_queue','test')
        self.assertEqual(len(self.q),0)

    def test_send(self):
        ''' send message '''
        self.send_message()
        self.assertEqual(len(self.q),1)
        capture(call_command,'process_mail_queue','test')
        self.assertEqual(len(self.q),0)



