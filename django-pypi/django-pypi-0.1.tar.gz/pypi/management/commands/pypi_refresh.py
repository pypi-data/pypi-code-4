from celery import group
from django.core.management.base import NoArgsCommand
from pypi.tasks import update_packages


class Command(NoArgsCommand):
    default_apps = None

    def handle_noargs(self, **options):
        print "Scheduling Celery to download all of pypi."
        update_packages.apply_async()
        print "Done"
