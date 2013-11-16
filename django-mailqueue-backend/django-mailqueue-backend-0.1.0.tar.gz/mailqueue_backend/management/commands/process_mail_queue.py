from mailqueue_backend.mail.smtp import QueuedEmailBackend

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

class Command(BaseCommand):
    args = ''
    help = 'Process the mail queue'

    def handle(self, *args, **options):
        test = 'test' in args
        sent,discarded,length = QueuedEmailBackend(fail_silently=settings.DEBUG,
            test=test).send_queued_messages()
        print('{0} message{3} sent and {2} message{4} discarded out of {1} message{5}.'
            .format(sent,length,discarded,"s"[sent==1:],"s"[discarded==1:],
            "s"[length==1:]))
