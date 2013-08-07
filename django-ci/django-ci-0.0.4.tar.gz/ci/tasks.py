from socketio_server.utils import send_socketio
import celery
import subprocess


@celery.task
def start_test(name, branch, task_id=None):
    send_socketio("", "test_start", dict(
        name=name,
        branch=branch,
        task_id=task_id,
    ))

    process = subprocess.Popen(["python", "manage.py", "citests",
        name, branch], stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    response = process.communicate()

    send_socketio("", "test_end", dict(
        name=name,
        branch=branch,
        response=response,
        task_id=task_id,
    ))
