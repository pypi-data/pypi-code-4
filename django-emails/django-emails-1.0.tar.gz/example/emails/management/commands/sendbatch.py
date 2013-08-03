from django.core.management.base import NoArgsCommand

from emails.engine import MailSender


class Command(NoArgsCommand):
    help = 'Send the next batch of mass emails.'

    def handle(self, *args, **options):
        mail_sender = MailSender()
        self.stdout.write(mail_sender.send_batch()+"\n")