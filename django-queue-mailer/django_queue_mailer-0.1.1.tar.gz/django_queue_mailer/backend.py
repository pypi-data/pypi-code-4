from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.base import BaseEmailBackend
from django_queue_mailer.models import Queue


class DbBackend(BaseEmailBackend):
    def send_messages(self, email_messages, app=None):
        num_sent = 0
        for message in email_messages:

            queue = Queue()
            queue.subject = message.subject
            queue.to_address = ', '.join(message.to)
            queue.bcc_address = ', '.join(message.bcc)
            queue.from_address = message.from_email
            queue.content = message.body

            #TODO How to add html content
            #queue.html_content = message.

            if app:
                queue.app = app

            queue.save()

            num_sent += 1
        return num_sent
