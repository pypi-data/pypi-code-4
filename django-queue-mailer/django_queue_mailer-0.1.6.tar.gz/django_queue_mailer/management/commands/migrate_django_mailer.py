import base64
import pickle
from django.core.management.base import BaseCommand, CommandError
from django.db import models, DatabaseError
from datetime import datetime
from django_queue_mailer.models import Log


PRIORITIES = (
    ("1", "high"),
    ("2", "medium"),
    ("3", "low"),
    ("4", "deferred"),
)

RESULT_CODES = (
    ("1", "success"),
    ("2", "don't send"),
    ("3", "failure"),
    # @@@ other types of failure?
)


def db_to_email(data):
    if data == u"":
        return None
    else:
        try:
            return pickle.loads(base64.decodestring(data))
        except Exception:
            try:
                # previous method was to just do pickle.dumps(val)
                return pickle.loads(data.encode("ascii"))
            except Exception:
                return None


class MessageLog(models.Model):
    message_data = models.TextField()
    when_added = models.DateTimeField()
    priority = models.CharField(max_length=1, choices=PRIORITIES)
    when_attempted = models.DateTimeField(default=datetime.now)
    result = models.CharField(max_length=1, choices=RESULT_CODES)
    log_message = models.TextField()

    class Meta:
        db_table = 'mailer_messagelog'

    @property
    def email(self):
        return db_to_email(self.message_data)

    @property
    def to_addresses(self):
        email = self.email
        if email is not None:
            return u", ".join(email.to)
        else:
            return []

    @property
    def subject(self):
        email = self.email
        if email is not None:
            return email.subject
        else:
            return ""

    @property
    def from_address(self):
        email = self.email
        if email is not None:
            return email.from_email
        else:
            return []

    @property
    def body(self):
        email = self.email
        if email is not None:
            return email.body
        else:
            return ""

    @property
    def body_html(self):
        email = self.email
        try:
            for alternative in email.alternatives:
                if alternative[1] == 'text/html':
                    return alternative[0]
        except AttributeError:
            return ""


class Command(BaseCommand):
    help = 'Migrate Message logs from django-mailer.'

    def handle(self, *args, **options):
        try:
            migrated = 0
            for old_log in MessageLog.objects.all():

                print old_log.subject
                print old_log.from_address

                new_log = Log()
                new_log.message_id = 'django-mailer-imported'
                new_log.subject = old_log.subject
                new_log.to_address = old_log.to_addresses
                new_log.from_address = old_log.from_address
                new_log.content = old_log.body
                new_log.html_content = old_log.body_html
                new_log.sent = old_log.when_attempted
                new_log.save()
                migrated += 1

            print '%s log messages successfully migrated from django-mail to django-query-mailer' % migrated

        except DatabaseError:
            raise CommandError('Unable to migrate as django-mailer as table mailer_messagelog was not found')
