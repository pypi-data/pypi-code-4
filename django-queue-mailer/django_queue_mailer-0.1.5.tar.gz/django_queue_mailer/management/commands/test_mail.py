from django.core.management import BaseCommand
from django_queue_mailer.models import Queue


class Command(BaseCommand):
    help = 'Create new entry in mail queue'

    def handle(self, *args, **options):

        new_message = Queue()
        new_message.subject = "Testing subject"
        new_message.to_address = "nobody@example.com, noone@example.com"
        new_message.bcc_address = "blindcopy@example.com"
        new_message.from_address = "hello@example.com"
        new_message.content = "Mail content"
        new_message.html_content = "<h1>Mail Content</h1>"
        new_message.app = "someapp"
        new_message.save()

