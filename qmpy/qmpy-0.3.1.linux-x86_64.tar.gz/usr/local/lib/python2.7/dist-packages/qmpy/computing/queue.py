#!/usr/bin/env python


from django.db import models
import json
import os.path
import time
from datetime import datetime, timedelta
import random

from resources import Project, Account, Allocation
import qmpy

class TaskError(Exception):
    '''A project was needed but not provided'''

class Task(models.Model):
    '''
    Model for a Task to be done. A Task consists of a module, which is the name
    of a computing script. 

    The Task.state attribute indicates:
        -2  :   error
        -1  :   held
        0   :   ready to advance
        1   :   running
        2   :   done

    Database Attributes:
        module      : name of a computing script - must correspond to a
                      qmpy.computing.script function. 
        args        : a json format string of a sequence of arguments to a
                      function.
        state       : int
        priority    : The priority of a task (float)

        entry       : Entry object
        project_set : QuerySet of Projects

        created     : DateTime field populated when the task is created.
        finished    : DateTeim field populated when the task is completed.
    '''
    module = models.CharField(max_length=60)
    args = models.CharField(max_length=100, blank=True)
    state = models.IntegerField(default=0)
    priority = models.IntegerField(default=50)
    created = models.DateTimeField(blank=True, auto_now_add=True)
    finished = models.DateTimeField(blank=True, null=True)

    entry = models.ForeignKey('Entry')
    project_set = models.ManyToManyField(Project, null=True)

    _projects = None

    class Meta:
        app_label = 'qmpy'
        db_table = 'tasks'

    def save(self, *args, **kwargs):
        super(Task, self).save(*args, **kwargs)
        self.project_set = [ Project.get(p) for p in self.projects ]

    @property
    def projects(self):
        '''List of related projects.'''
        if self._projects is None:
            self._projects = list(self.project_set.all())
        return self._projects

    @projects.setter
    def projects(self, projects):
        self._projects = projects

    @property
    def eligible_to_run(self):
        if self.state != 0:
            return False
        if self.entry.holds:
            return False
        if not any( p.active for p in self.project_set.all()):
            return False
        return True

    def get_project(self):
        projects = [ p for p in self.projects if p.active ]
        return random.choice(projects)

    @staticmethod
    def create(entry, module='standard', args=[],
            priority=None, projects=None): 
        if projects is None:
            projects = entry.projects
        elif isinstance(projects, basestring):
            projects = Project.objects.get(name=projects)
        if priority is None:
            priority = len(entry.input)
        task, created = Task.objects.get_or_create(entry=entry, 
                args=json.dumps(args), module=module)
        if created:
            task.projects = projects
        else:
            task.projects += projects

        task.priority = priority
        return task

    def complete(self):
        '''Sets the Task state to 2 and populates the finished field.'''
        self.state = 2
        self.finished = datetime.now()

    def __str__(self):
        return '%s (%s: %s)' % (self.module, self.entry, self.entry.path)

    @property
    def jobs(self):
        '''List of jobs related to the task.'''
        return self.job_set.all()

    @property
    def errors(self):
        '''List of errors encountered by related calculations.'''
        return self.entry.errors

    def get_jobs(self, project=None, allocation=None, account=None):
        '''
        Calls the task's entry's "do" method, with first argument as the tasks
        module, and subsequent arguments as the args list. If there is nothing
        left to do, returns an empty sequence.
        '''
        if project is None:
            project = self.get_project()
            while not project:
                print '   -not project'
                time.sleep(30)
                project = self.get_project()
        if allocation is None:
            allocation = project.get_allocation()
            while not allocation:
                print '   -not allocation'
                time.sleep(30)
                allocation = project.get_allocation()
        if account is None:
            account = allocation.get_account(users=list(project.users.all()))

        calc = self.entry.do(self.module, args=json.loads(self.args))
        jobs = []
        #for calc in calcs:
        if calc.instructions:
            self.state = 1
            new_job = Job.create(
                task=self, 
                allocation=allocation, 
                account=account,
                entry=self.entry,
                **calc.instructions)
            jobs.append(new_job)
            calc.save()
        elif calc.converged:
            self.complete()
        else:
            self.state = -1
        return jobs

class Job(models.Model):
    '''
    Job model. Corresponds to a calculation on a compute cluster.

    Job codes:
        -1  :   error
        0   :   eeady to submit
        1   :   running
        2   :   done

    Database attributes:
        qid
        walltime
        path
        run_path
        ncpus

        task
        account
        allocation
        entry

        created
        finished
    '''
    qid = models.IntegerField(default=0)
    walltime = models.DateTimeField(blank=True)
    path = models.CharField(max_length=200)
    run_path = models.CharField(max_length=200)
    ncpus = models.IntegerField(blank=True)
    created = models.DateTimeField(blank=True, auto_now_add=True)
    finished = models.DateTimeField(blank=True, null=True)
    state = models.IntegerField(default=0)

    task = models.ForeignKey(Task)
    entry = models.ForeignKey('Entry')
    account = models.ForeignKey(Account)
    allocation = models.ForeignKey(Allocation)

    class Meta:
        app_label = 'qmpy'
        db_table = 'jobs'

    @staticmethod
    def create(task=None, allocation=None, entry=None,
            account=None,
            path=None, 
            walltime=3600, serial=None,
            header=None,
            mpi=None, binary=None, pipes=None,
            footer=None):

        if entry is None:
            entry = task.entry

        assert isinstance(allocation, Allocation)
        assert isinstance(task, Task)
        assert path is not None

        if account is None:
            account = allocation.get_account()
        
        job = Job(path=path, walltime=walltime, 
                allocation=allocation,
                account=account,
                entry=entry,
                task=task)

        #if walltime < 3600:
        #    nodes = 1
        #    ppn = int(walltime/3600.*job.account.host.ppn)
        #    walltime = walltime/ppn
        #else:
        #    ppn = job.account.host.ppn
        #    nodes = 1+int(walltime/float(job.account.host.walltime))
        #    walltime = walltime/float(ppn*nodes)
        
        if serial:
            ppn = 1
            nodes = 1
            walltime = 3600*24
        else:
            nodes = 1
            ppn = job.account.host.ppn
            walltime = job.account.host.walltime
            
        binary = job.account.host.get_binary(binary)
        if not binary:
            raise AllocationError

        sec = timedelta(seconds=walltime)
        d = datetime(1,1,1) + sec
        job.walltime = d
        walltime = '%02d:%02d:%02d:%02d' % (
                d.day-1, 
                d.hour, 
                d.minute,
                d.second)

        qp = qmpy.INSTALL_PATH + '/configuration/qfiles/'
        text = open(qp+job.account.host.sub_text+'.q', 'r').read()
        qfile = text.format(
                host=allocation.host.name,
                key=allocation.key, name=job.description,
                walltime=walltime, nodes=nodes, ppn=ppn,
                header=header,
                mpi=mpi, binary=binary, pipes=pipes,
                footer=footer)

        qf=open(job.path+'/auto.q', 'w')
        qf.write(qfile)
        qf.close()
        job.ncpus = ppn*nodes
        job.run_path = job.account.run_path+'/'+job.description
        return job

    @property
    def walltime_expired(self):
        from datetime import datetime, timedelta
        elapsed = datetime.now() - self.created
        if elapsed.total_seconds() > self.walltime:
            return True
        else:
            return False

    @property
    def subdir(self):
        return self.path.replace(self.entry.path, '')

    @property
    def description(self):
        return '{entry}_{subdir}_{uniq}'.format(
                entry=self.entry.id,
                subdir=self.subdir.strip('/').replace('/','_'),
                uniq='-'.join(json.loads(self.task.args)))

    def __str__(self):
        return '%s on %s' % (self.description, self.account)

    def is_done(self):
        if datetime.now() + timedelta(seconds=-600) > self.created:
            return False

        return not ( self.qid in self.account.host.running_now )

    def submit(self, verbosity=0):
        self.created = datetime.now()
        self.qid = self.account.submit(path=self.path,
                run_path=self.run_path,
                qfile='auto.q', verbosity=verbosity)
        self.task.state = 1
        self.state = 1

    def collect(self, verbosity=0):
        if self.account.host.state == -1:
            return
        self.task.state = 0
        self.task.save()
        self.state = 2
        self.account.copy(move=True,
                to='local', destination=self.path,
                folder=self.run_path, file='*')
        self.account.execute('rm -rf %s' % self.run_path, ignore_output=True)
        self.finished = datetime.now()

