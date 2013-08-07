from ci.models import CiProject
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, name, branch, *args, **options):
        project = CiProject.objects.get(name=name, branch=branch)
        project.testrun_set.all().delete()
        project.test()
