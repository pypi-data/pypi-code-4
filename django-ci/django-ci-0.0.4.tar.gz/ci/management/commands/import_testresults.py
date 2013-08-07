from ci.models import CiProject, TestModule, TestRun
from django.conf import settings
from django.core.management.base import BaseCommand
import json
import os


class Command(BaseCommand):
    help = 'loads testresults.json into database'

    def handle(self, name="local_site", branch="master", filename="testresults.json", **options):

        fileh = open(filename, "r")

        results = json.loads(fileh.read())

        project = CiProject.objects.get_or_create(
            name=name,
            branch=branch,
            defaults=dict(
                url=os.path.abspath(os.path.join(settings.DIRNAME, ".."))
            )
        )[0]

        for module, tests in results.items():
            module = TestModule.objects.get_or_create(name=module)[0]

            for test in tests:
                run = TestRun.objects.get_or_create(
                    project=project,
                    module=module,
                    name=test['name'],
                )[0]
                for name, value in dict(
                    status=test['status'],
                    description=test.get("description"),
                    error=test.get("error")
                ).items():
                    setattr(run, name, value)
                run.save()

