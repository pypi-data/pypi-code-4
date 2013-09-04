"""
Django command to clean up expired sessions from database

(alternative to built-in cleanup command)

See https://github.com/isnotajoke/django-batch-session-cleanup

author: Kevan Carstensen <kevan@isnotajoke.com>
"""

import datetime
import time

from optparse import make_option

from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
from django.db import connection, transaction

# replaces td.total_seconds() on pre-2.7 platforms
def timedelta_to_seconds(td):
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6

class BatchSessionCleanupCommand(BaseCommand):
    sql = "DELETE FROM django_session WHERE expire_date < NOW() LIMIT %s;"

    help = "Delete expired sessions in batches (alternative to built-in cleanup command)"

    option_list = BaseCommand.option_list + (
        make_option("--batch-size",
            action='store',
            dest='batch_size',
            type='int',
            default=50000,
            help="Delete sessions in batches no larger than BATCH_SIZE"),
        make_option("--sleep-time",
            action='store',
            dest='sleep_time',
            type='float',
            default=2.0,
            help="# of seconds to sleep in between batches"),
    )

    def handle(self, *args, **options):
        self.process_options(options)

        # Total # of sessions in the database
        self.total_session_count    = Session.objects.all().count()
        # Total # of sessions deleted by the delete process
        self.deleted_session_count = 0
        # Number of batches run
        self.batch_count            = 0
        self.start_time             = datetime.datetime.now()

        self.purge_sessions()

        self.print_results()

    def process_options(self, options):
        self.batch_size  = options['batch_size']
        self.sleep_time  = options['sleep_time']
        self.verbose     = ('verbosity' in options and
                            int(options['verbosity']) > 1)

        if self.verbose:
            self.stdout.write("batch-session-cleanup ready\n")
            self.stdout.write("batch size: %d\n" % (self.batch_size))
            self.stdout.write("sleep time: %.2f\n" % (self.sleep_time))

    def purge_sessions(self):
        cursor = connection.cursor()

        deleted_count = self.batch_size

        while deleted_count == self.batch_size:
            self.batch_count += 1
            start_time = datetime.datetime.now()

            deleted_count = cursor.execute(self.sql, [int(self.batch_size)])
            transaction.commit_unless_managed()

            self.deleted_session_count += deleted_count

            duration = datetime.datetime.now() - start_time
            duration_s = timedelta_to_seconds(duration)

            if self.verbose:
                self.stdout.write("deleted %d sessions in %d seconds\n" % (deleted_count, duration_s))
                self.stdout.write("sleeping for %d seconds\n" % self.sleep_time)

            time.sleep(self.sleep_time)

    def print_results(self):
        self.stdout.write("Deleted %d sessions out of %d "
                          "total sessions\n" %
                            (self.deleted_session_count,
                             self.total_session_count))
        self.stdout.write("Ran %d batches\n" % self.batch_count)

        elapsed_time = datetime.datetime.now() - self.start_time

        self.stdout.write("Total execution time was %d seconds\n" % timedelta_to_seconds(elapsed_time))
