from datetime import datetime, timedelta
import random
import subprocess
import os
import os.path
import time

from django.db import models
from django.contrib.auth.models import User

from qmpy.db.custom import DictField

class AllocationError(Exception):
    '''Problem with the allocation'''

class SubmissionError(Exception):
    '''Failed to submit a job'''

class Host(models.Model):
    '''
    Host model - stores all host information for a cluster.

    Stored attributes:
        name
        ip_address
        hostname
        binaries    :   dict of binary names and paths 
        ppn         :   # of processors per node (int)
        nodes
        walltime
        sub_script
        sub_text
        check_queue
        checked_time
        running
        utilization
    '''
    name = models.CharField(max_length=20, db_index=True)
    ip_address = models.CharField(max_length=120)
    hostname = models.CharField(max_length=120)
    binaries = DictField()
    ppn = models.IntegerField(default=8)
    nodes = models.IntegerField(default=30)
    walltime = models.IntegerField(default=3600*24)
    sub_script = models.CharField(max_length=120)
    sub_text = models.TextField(default='/usr/local/bin/qsub')
    check_queue = models.CharField(max_length=180,
            default='/usr/local/maui/bin/showq')
    checked_time = models.DateTimeField(default=datetime.min)
    running = DictField(blank=True, null=True)
    utilization = models.IntegerField(default=0)
    state = models.IntegerField(default=1)

    class Meta:
        app_label = 'qmpy'
        db_table = 'hosts'

    def __str__(self):
        return self.name

    @classmethod
    def interactive_create(cls):
        '''
        Classmethod to create a Host model. Script will ask you questions about
        the host to add, and will return the created Host.

        '''
        host = {}
        host['name'] = raw_input('Hostname:')
        if cls.objects.filter(name=host['name']).exists():
            print 'Host by that name already exists!'
            exit(-1)
        host['ip_address'] = raw_input('IP Address:')
        if cls.objects.filter(ip_address=host['ip_address']).exists():
            print 'Host at that address already exists!'
            exit(-1)
        host['ppn'] = raw_input('Processors per node:')
        host['nodes'] = raw_input('Max nodes to run on:')
        host['sub_script'] = raw_inputs('Command to submit a script '+
                '(e.g. /usr/local/bin/qsub):')
        host['check_queue'] = raw_input('Command for showq (e.g.'+
                '/usr/local/maui/bin/showq):')
        host['sub_text'] = raw_input('Path to qfile template:')
        h = cls(**host)
        h.save()

    @property
    def accounts(self):
        return list(self.account_set.all())

    @property
    def jobs(self):
        jobs = []
        for acct in self.accounts:
            jobs += list(acct.job_set.filter(state=1))
        return jobs

    @property
    def active(self):
        if self.state < 1:
            return False
        elif self.utilization > self.nodes*self.ppn:
            return False
        else:
            return True

    @property
    def percent_utilization(self):
        return 100. * float(self.utilization) / (self.nodes*self.ppn)

    @property
    def utilization(self):
        util = 0
        for acct in self.account_set.all():
            for job in acct.job_set.filter(state=1):
                util += job.ncpus
        return util

    @property
    def qfile(self):
        return open(self.sub_text).read()

    def get_binary(self, key):
        return self.binaries[key]

    def check_host(self):
        '''Pings the host to see if it is online. Returns False if it is
        offline.'''
        ret = subprocess.call("ping -c 1 -w 1 %s" % self.ip_address,
                shell=True,
                stdout=open('/dev/null', 'w'),
                stderr=subprocess.STDOUT)
        if ret == 0:
            return True
        else:
            self.state = -2
            self.save()
            return False

    @property
    def running_now(self):
        if datetime.now() + timedelta(seconds=-30) > self.checked_time:
            self.check_running()
        return self.running

    def check_running(self, verbosity=0):
        '''
        Uses the hosts data and one of the associated accounts to check the PBS
        queue on the Host. If it has been checked in the last 2 minutes, it
        will return the previously returned result.

        '''
        self.checked_time = datetime.now()
        if self.state < 0:
            self.running = {}
            self.save()
            return
        account = random.choice(self.accounts)
        raw_data = account.execute(self.check_queue, verbosity=verbosity)
        running = {}
        if not raw_data:
            return
        for line in raw_data.split('\n'):
            if 'Active Jobs' in line:
                continue
            line = line.split()
            if len(line) != 9:
                continue
            try:
                running[int(line[0])] = {
                        'user':line[1],
                        'state':line[2],
                        'proc':int(line[3])}
            except:
                pass
        self.running = running
        self.save()
        
    def get_running(self):
        if self.running is not None:
            return self.running
        else:
            return {}

#===============================================================================#

class Account(models.Model):
    user = models.ForeignKey(User)
    host = models.ForeignKey(Host)
    username = models.CharField(max_length=20)
    run_path = models.CharField(max_length=120)

    state = models.IntegerField(default=1)
    class Meta:
        app_label = 'qmpy'
        db_table = 'accounts'

    def __str__(self):
        return '{user}@{host}'.format(user=self.user.username, 
                host=self.host.name)

    @property
    def active(self):
        if self.state < 1:
            return False
        elif not self.host.active:
            return False
        else:
            return True

    def submit(self, path=None, run_path=None, 
            qfile=None, verbosity=0):
        self.execute('mkdir %s' % run_path, verbosity=verbosity,
                ignore_output=True)
        self.copy(folder=path, file='*',
                destination=run_path,
                verbosity=verbosity)
        cmd = 'cd {path} && {sub} {qfile}'.format(
                path=run_path, 
                sub=self.host.sub_script,
                qfile=qfile)
        stdout = self.execute(cmd, verbosity=verbosity)
        jid = int(stdout.split()[0].split('.')[0])
        if self.host.name == 'quest':
            time.sleep(60)
        return jid

    def execute(self, command='exit 0', verbosity=0, ignore_output=False):
        ssh = 'ssh {user}@{host} "{cmd}"'.format(
                user=self.username,
                host=self.host.ip_address,
                cmd=command)

        if verbosity > 0:
            print ssh

        call = subprocess.Popen(ssh, shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        stdout,stderr = call.communicate()

        if verbosity > 0:
            print 'stdout:', stdout
            print 'stderr:', stderr
        if stderr and not ignore_output:
            print 'WARNING:'
            print stderr
        return stdout

    def copy(self, destination=None, to=None, # where to send the stuff
            fr=None, file=None, folder=None, # what to send
            clear_dest_dir=False, verbosity=0, move=False): # some conditions on sending it

        if destination is None:
            destination = self.run_path
        if to is None:
            to = self
        if fr is None:
            if to == 'local':
                fr = self
            else:
                fr = 'local'

        assert (isinstance(to, Account) or to == 'local')
        assert (isinstance(fr, Account) or fr == 'local')

        send_dir = False
        if file is None and folder is None:
            print 'Must specify something to copy'
        elif file is None:
            send_dir = True
        elif folder is None:
            folder = os.path.dirname(file)
            file = os.path.basename(file)
        
        if clear_dest_dir:
            if to == 'local':
                command = subprocess.Popen('rm -f %s/*' % destination,
                                                  stderr=subprocess.PIPE,
                                                  stdout=subprocess.PIPE)
                stdout, stderr = command.communicate()
            else:
                stdout, stderr = self.execute('rm -f %/*' % destination)
            if verbosity:
                print 'output:', stdout
            
        if fr == 'local':
            scp = 'scp '
        else:
            scp = 'scp {user}@{host}:'.format(
                    user=fr.username, host=fr.host.ip_address)

        if not file:
            scp += '-r '

        if send_dir:
            scp += os.path.abspath(folder)
        else:
            scp += '{path}/{file}'.format(
                    path=os.path.abspath(folder), file=file)

        if to == 'local':
            scp += ' '+destination
        else:
            scp += ' {user}@{host}:{path}'.format(
                user=to.username, host=to.host.ip_address, 
                path=os.path.abspath(destination))

        if verbosity > 0:
            print 'copy command:', scp
        cmd = subprocess.Popen(scp,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        stdout, stderr = cmd.communicate()
        if verbosity:
            print 'stdout:', stdout
            print 'stderr:', stderr

        if move:
            if send_dir:
                rmcmd = 'rm -rf {path}'.format(path=os.path.abspath(folder))
            else:
                rmcmd = 'rm -f {path}/{file}'.format(file=file,
                        path=os.path.abspath(folder))
            if verbosity > 0:
                print 'wiping source: ', rmcmd
            stdout = fr.execute(rmcmd)
            if verbosity > 0:
                print 'output:', stdout

#===============================================================================#

class Allocation(models.Model):
    name = models.CharField(max_length=50, db_index=True)
    key = models.CharField(max_length=100, default='', blank=True, null=True)

    host = models.ForeignKey(Host, null=True)
    users = models.ManyToManyField(User, null=True)
    state = models.IntegerField(default=1)
    
    class Meta:
        app_label = 'qmpy'
        db_table = 'allocations'

    def __str__(self):
        return self.name
    
    @classmethod
    def create_interactive(cls):
        name = raw_input('Name your allocation:')
        if cls.objects.filter(name=name).exists():
            print 'Allocation by that name already exists!'
            exit(-1)
        host = raw_input('Which cluster is this allocation on?')
        if not Host.objects.filter(name=host).exists():
            print "This host doesn't exist!"
            exit(-1)
        host = Host.objects.get(name=host)
        alloc = cls(name=name, host=host)
        alloc.save()
        print 'Now we will assign users to this allocation'
        for acct in Account.objects.filter(host=host):
            inc = raw_input('Can %s use this allocation? y/n [y]:' % 
                    acct.user.name )
            if inc == 'y' or inc == '':
                alloc.users.add(acct.user)
        print 'If this allocation requires a special password, enter',
        key = raw_input('it now:')
        alloc.key=key
        alloc.save()

    @property
    def active(self):
        if self.state < 1:
            return False
        elif not self.host.active:
            return False
        else:
            return True

    def get_user(self):
        return random.choice(self.users.filter(state=1))

    def get_account(self, users=None):
        if users is None:
            users = self.users.filter(state=1).all()
        user = random.choice(list(users))
        return user.account_set.get(host=self.host)

    @property
    def percent_utilization(self):
        return self.host.percent_utilization

#===============================================================================#

class Project(models.Model):
    name = models.CharField(max_length=60)
    priority = models.IntegerField(default=0)

    users = models.ManyToManyField(User)
    allocations = models.ManyToManyField(Allocation)
    state = models.IntegerField(default=1)
    class Meta:
        app_label = 'qmpy'
        db_table = 'projects'

    def __str__(self):
        return self.name

    @classmethod
    def get(cls, name):
        if isinstance(name, cls):
            return name
        proj, new = cls.objects.get_or_create(name=name)
        if new:
            proj.save()
        return proj

    @property
    def completed(self):
        return self.task_set.filter(state=2)

    @property
    def running(self):
        from queue import Job
        return Job.objects.filter(state=1, task__project_set=self)

    @classmethod
    def interactive_create(cls):
        name = raw_input('Name your project: ')
        if cls.objects.filter(name=name).exists():
            print 'Project by that name already exists!'
            exit(-1)
        proj = cls(name=name)
        proj.save()
        proj.priority = raw_input('Project priority (1-100): ')
        users = raw_input('List project users (e.g. sjk648 jsaal531 bwm291): ')
        for u in users.split():
            if not User.objects.filter(name=u).exists():
                print 'User named', u, 'doesn\'t exist!'
            else:
                proj.users.add(User.objects.get(name=u))

        alloc = raw_input('List project allocations (e.g. byrd victoria b1004): ')
        for a in alloc.split():
            if not Allocation.objects.filter(name=a).exists():
                print 'Allocation named', a, 'doesn\'t exist!'
            else:
                proj.allocations.add(Allocation.objects.get(name=a))

    @property
    def active(self):
        if self.state < 0:
            return False
        elif not any( a.active for a in self.allocations.all() ):
            self.state = 0
            self.save()
            return False
        else:
            if self.state != 1:
                self.state = 1
                self.save()
            return True

    def get_allocation(self):
        available = [ a for a in self.allocations.all() if a.active ]
        if available:
            return random.choice(available)
        else:
            return []
