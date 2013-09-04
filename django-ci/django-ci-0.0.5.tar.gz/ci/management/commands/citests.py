from ci.models import CiBranch
from django.core.management.base import BaseCommand
import sys


class Command(BaseCommand):

    def handle(self, name, branch, *args, **options):
        print 'citests'
        print "=" * 20
        sys.stdout.flush()

        print "getting branch"
        sys.stdout.flush()
        project = CiBranch.objects.get(project__name=name, name=branch)

        print "testing"
        sys.stdout.flush()
        project.test()
