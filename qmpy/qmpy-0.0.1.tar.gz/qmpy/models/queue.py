from django.db import models
from entry import Entry
from resources import Project, Account, Allocation
from datetime import datetime, timedelta
import json
import os.path
import time
import sys

'''
Task:
    state = -2; error
    state = -1; held
    state = 0; ready to advance
    state = 1; running
    state = 2; done

Job:
    state = -1; error
    state = 0; ready to submit
    state = 1; running
    state = 2; done
'''

class Task(models.Model):
    module = models.CharField(max_length=60)
    args = models.CharField(max_length=255, blank=True)
    state = models.IntegerField(default=0)
    priority = models.IntegerField(default=100)
    log = models.TextField(default='')

    entry = models.ForeignKey(Entry)
    project = models.ForeignKey(Project, null=True)

    class Meta:
        db_table = 'tasks'

    @property
    def eligible_to_run(self):
        if self.state != 0:
            return False
        if self.entry.get_holds():
            return False
        if not self.project.active:
            return False
        return True

    @staticmethod
    def create(entry, module='standard', args=[],
            priority=None, project=None, replace_project=True):
        if project is None:
            project = entry.project
        elif isinstance(project, basestring):
            project = Project.objects.get(name=project)
        if priority is None:
            priority = entry.natoms
        task, created = Task.objects.get_or_create(entry=entry, 
                args=json.dumps(args), module=module)
        if created:
            print 'Created %s' % task
            task.project = project
            task.log += 'created on %s' % datetime.now()
        elif replace_project:
            task.project = project

        task.priority = priority
        return task

    def __str__(self):
        return '%s on %s' % (self.module, self.entry.path)

    @property
    def jobs(self):
        return self.job_set.all()

    @property
    def errors(self):
        return self.entry.errors

    def get_jobs(self, allocation=None):
        #if not self.eligible_to_run:
        #    return []

        if allocation is None:
            allocation = self.project.get_allocation()
            while not allocation:
                time.sleep(30)
                allocation = self.project.get_allocation()

        #if self.project:
        account = allocation.get_account(project=self.project)
        #else:
        #    account = allocation.get_account()

        calc = self.entry.do(self.module, args=json.loads(self.args))
        jobs = []
        #for calc in calcs:
        if calc.instructions:
            self.log += 'spawned jobs on %s' % self.module
            self.state = 1
            jobs.append(Job.create(
                task=self, 
                allocation=allocation, 
                account=account,
                entry=self.entry,
                **calc.instructions))
            calc.save()
        elif calc.done:
            print '   -%s is done!' % self
            self.log += 'completed on %s' % datetime.now()
            self.state = 2
        else:
            print '   -Holding task', self
            self.state = -1
        return jobs


class Job(models.Model):
    qid = models.IntegerField(default=0)
    walltime = models.DateTimeField(blank=True)
    path = models.CharField(max_length=200)
    run_path = models.CharField(max_length=200)
    ncpus = models.IntegerField(blank=True)
    start_time = models.DateTimeField(blank=True, auto_now_add=True)
    state = models.IntegerField(default=0)
    log = models.TextField(default='')

    task = models.ForeignKey(Task)
    entry = models.ForeignKey(Entry)
    account = models.ForeignKey(Account)
    allocation = models.ForeignKey(Allocation)

    class Meta:
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

        text = open(job.account.host.sub_text, 'r').read()
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
        job.log += 'created on %s' % datetime.now()
        return job

    @property
    def walltime_expired(self):
        from datetime import datetime, timedelta
        elapsed = datetime.now() - self.start_time
        if elapsed.total_seconds() > self.walltime:
            return True
        else:
            return False

    @property
    def description(self):
        return '{entry}_{subdir}_{uniq}'.format(
                entry=self.entry.id,
                subdir=self.path.replace(self.entry.path, '').strip('/'),
                uniq=','.join(json.loads(self.task.args)))

    def __str__(self):
        return '%s on %s' % (self.description, self.account)

    def is_done(self):
        if self.account.host.name in ['hopper']:
            return False

        if datetime.now() + timedelta(seconds=-120) < self.start_time:
            return False


        if self.account.host.checked_time < datetime.now()+timedelta(seconds=-120):
            self.account.host.check_running()

        if unicode(self.qid) in self.account.host.get_running():
            return False
        else:
            return True

    def submit(self, verbosity=0):
        self.start_time = datetime.now()
        self.qid = self.account.submit(path=self.path,
                run_path=self.run_path,
                qfile='auto.q', verbosity=verbosity)
        self.task.state = 1
        self.state = 1
        self.log += 'sumitted on %s' % datetime.now()

    def collect(self, verbosity=0):
        if self.account.host.state == -1:
            return
        print '   -collecting', self.description, 'to', self.entry.path
        self.task.state = 0
        self.task.save()
        self.state = 2
        self.account.copy(move=True,
                to='local', destination=self.path,
                folder=self.run_path, file='*')
        self.account.execute('rm -rf %s &> /dev/null' % self.run_path)
        self.log += 'collected on %s' % datetime.now()

