import json
import os.path
import time
import sys
import logging
from datetime import datetime, timedelta

import django.db as ddb

from qmpy.computing.queue import Task, Job
from qmpy.computing.resources import *
from qmpy.utils.daemon import Daemon
from qmpy.analysis.vasp.calculation import VaspError

logger = logging.getLogger(__name__)

def check_die():
    if os.path.exists('/home/sjk648/die'):
        exit(0)

class JobManager(Daemon):
    '''
    Class to manage collection of running Job objects. When running, it
    collects any Job whose is_done method evaluates to True. While the manager
    is running (as a Daemon or normally) it will look for a file named "die" in
    the home directory of the user who initialized the manager, and if found it
    will stop cleanly.

    '''
    def run(self):
        os.umask(022)
        while True:
            if len(ddb.connection.queries) > 10000:
                ddb.connection.queries = []
            jobs = Job.objects.filter(state=1, account__host__state=1,
                    created__lt=datetime.now() - timedelta(seconds=-300))
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
    '''
    Class to manage creation of Job objects from uncompleted Tasks. While
    running it finds the next available Task (based on additional keyword
    arguments) and attempts to submit all Jobs return by the tasks get_jobs()
    method. While the manager is running (as a Daemon or normally) it will 
    look for a file named "die" in the home directory of the user who 
    initialized the manager, and if found it will stop cleanly.

    Conditions for Task eligibility are:
        - A resource assosiated with the Task (via its projects list) has CPUs
          available.
        - if the manager is called with the project keyword, only Tasks
          associated with that project will be run
        - if the manager is called with the path keyword, only Tasks whose
          entry contain the path or path fragment will be run.
    '''
    def run(self, project=None, path=None, id=None):
        os.umask(022)
        while True:
            if len(ddb.connection.queries) > 10000:
                ddb.connection.queries = []
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
                check_die()
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


