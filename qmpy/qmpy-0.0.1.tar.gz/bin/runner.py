from qmpy import *
from datetime import datetime, timedelta
import json
import os.path
import time
import sys

def check_die():
    if os.path.exists('/home/sjk648/die'):
        exit(0)

def collect_jobs():
    print 'collecting all jobs'
    for j in Job.objects.filter(state=1):
        print j
        check_die()
        j.collect()
        j.state = 2
        j.save()

def check_jobs():
    while True:
        jobs = Job.objects.filter(state=1, account__host__state=1)
        for job in jobs:    
            check_die()
            if job.is_done():
                print job
                job.collect()
                job.state = 2
                job.save()
        for i in range(20):
            time.sleep(1)
            check_die()


def check_tasks(project=None, path=None, id=None):
    while True:
        check_die()

        tasks = Task.objects.filter(state=0, 
                project__state=1,
                entry__holds='')
        if project:
            tasks = tasks.filter(project=project)
        if path:
            tasks = tasks.filter(entry__path__contains=path)
        if id:
            tasks = tasks.filter(id__endswith=id)
        tasks = tasks.order_by('priority')
        if project == 'questek':
            tasks = tasks.order_by('entry__path')
        #if project == 'icsd':
        #    tasks = tasks.filter(entry__natoms__lt=10)

        while not tasks.exists():
            print 'No tasks available'
            Project.objects.filter(state=0).update(state=1)
            for i in range(120):
                time.sleep(1)
                check_die()

            tasks = Task.objects.filter(state=0, 
                    project__state=1,
                    entry__holds='')
            if project:
                tasks = tasks.filter(project=project)
            if path:
                tasks = tasks.filter(entry__path__contains=path)
            if id:
                tasks = tasks.filter(id__endswith=id)
            tasks = tasks.order_by('priority')
            if project == 'questek':
                tasks = tasks.order_by('entry__path')
            #if project == 'icsd':
            #    tasks = tasks.filter(entry__natoms__lt=10)

        task = tasks[0]
        print task
        if not task.eligible_to_run:
            continue

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
            print '   -Submitting', job
            while not job.state == 1:
                #try:
                job.submit()
                #except Exception:
                #    print '    -submission error, waiting 30 seconds'
                #    time.sleep(30)
            job.save()
        task.save()

if __name__ == '__main__':
    if 'force' in sys.argv:
        collect_jobs()
    if 'collect' in sys.argv:
        check_jobs()
    if 'submit' in sys.argv:
        try:
            project = sys.argv.index('project')
            project = sys.argv[project+1]
        except ValueError:
            project = None

        try:
            path = sys.argv.index('path')
            path = sys.argv[path+1]
        except ValueError:
            path = None

        try:
            id = sys.argv.index('id')
            id = sys.argv[id+1]
        except ValueError:
            id = None

        check_tasks(project=project, path=path, id=id)
