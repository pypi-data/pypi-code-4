from socketio_server.utils import send_socketio
import celery
import subprocess
from ci.models import TestRun, CiBranch, CiProject, TestModule, NotificationPref
import logging
from django.utils.unittest.util import safe_str
from django.utils.encoding import force_text
from django.core.mail import send_mail


class DebugTask(celery.Task):
    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logging.error("Exception: %s\nArgs: %s, %s\nEinfo: %s", exc, args, kwargs, einfo)

        project = CiProject.objects.get(name=args[0])
        branch = CiBranch.objects.get(project=project, name=args[1])
        TestRun.objects.create(
            branch=branch,
            module=TestModule.objects.get_or_create(name="TestStartup")[0],
            name="Test Startup",
            status="fail",
            description="Tests failed to run",
            error="Exception: %s\nArgs: %s, %s\nEinfo: %s" %
                (exc, args, kwargs, einfo)
        )


@celery.task(base=DebugTask)
def start_test(name, branch, task_id=None):

    process = subprocess.Popen(["python", "manage.py", "citests",
        name, branch], stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    process.wait()
    response = process.communicate()

    send_socketio("", "test_end", dict(
        name=name,
        branch=branch,
        response=force_text(response),
        task_id=task_id,
    ))
