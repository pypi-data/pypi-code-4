import json
import os.path
import time
import sys
import logging
from datetime import datetime, timedelta

from qmpy.computing.queue import Task, Job
from qmpy.computing.resources import *
from qmpy.utils.daemon import Daemon
from qmpy.analysis.vasp.calculation import VaspError

logger = logging.getLogger(__name__)

def check_die():
    if os.path.exists('/home/sjk648/die'):
        exit(0)

class JobManager(Daemon):
    def run(self):
        while True:
            jobs = Job.objects.filter(state=1, account__host__state=1)
            for job in jobs:    
                check_die()
                if job.is_done():
                    print job
                    job.collect()
                    job.save()
            for i in range(20):
                time.sleep(1)
                check_die()

class TaskManager(Daemon):
    def run(self, project=None, path=None, id=None):
        while True:
            check_die()

            tasks = Task.objects.none()
            while not tasks.exists():
                if project:
                    tasks = Project.get(project).task_set.filter(state=0)
                else:
                    tasks = Task.objects.filter(project_set__state=1, state=0)
                tasks = tasks.exclude(entry__meta_data__type='hold')
                if tasks.exists():
                    break

                Project.objects.filter(state=0).update(state=1)
                for i in range(120):
                    time.sleep(1)
                    check_die()

            time.sleep(10)
            for task in tasks.order_by('priority')[:50]:
                if not task.eligible_to_run:
                    task.state = -1
                    task.save()
                    continue

                print task

                try:
                    jobs = task.get_jobs()
                except VaspError:
                    print '    -VASP Error.'
                    task.state = -1
                    task.save()
                    continue
                except Exception, err:
                    task.state = -1
                    task.save()
                    print '   -Unknown error!', err
                    continue

                for job in jobs:
                    while not job.state == 1:
                        try:
                            job.submit()
                        except Exception:
                            print '  -waiting 30 seconds to resubmit'
                            time.sleep(30)
                    job.save()
                task.save()
                task.entry.save()


