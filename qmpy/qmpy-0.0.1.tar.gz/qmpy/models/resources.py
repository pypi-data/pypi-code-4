'''Stores details about computational resources which are available to qmpy for
doing calculations.

All resource objects - users, hosts, accounts, allocations, and projects - have
a state variable which can take on the following values, with the following
meanings:
    1   :   active, ready to rock
    0   :   no resources available, i.e. will be reset to active again when
            resources free up
    -1  :   manually set to unavailable, i.e. will NOT be reset to active if
            resources are found to be available
    -2  :   bigger failure, also will not reset to active if found to be
            available.

'''

from datetime import datetime
import random
import subprocess
import os
import os.path
import time

from django.db import models

class AllocationError(Exception):
    '''Problem with the allocation'''

class SubmissionError(Exception):
    '''Failed to submit a job'''

class Host(models.Model):
    name = models.CharField(max_length=20, db_index=True)
    ip_address = models.CharField(max_length=120)
    hostname = models.CharField(max_length=120)
    binaries = models.TextField(default=json.dumps({}))
    ppn = models.IntegerField(default=8)
    nodes = models.IntegerField(default=30)
    walltime = models.IntegerField(default=3600*24)
    sub_script = models.CharField(max_length=120)
    sub_text = models.TextField(default='/usr/local/bin/qsub')
    check_queue = models.CharField(max_length=180,
            default='/usr/local/maui/bin/showq')
    checked_time = models.DateTimeField(default=datetime.min)
    running = models.TextField(blank=True)
    utilization = models.IntegerField(default=0)

    state = models.IntegerField(default=1)
    class Meta:
        db_table = u'hosts'

    def __str__(self):
        return self.name

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
        bins = json.loads(self.binaries)
        return bins.get(key, None)

    def check_host(self):
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

    def check_running(self, verbosity=0):
        self.checked_time = datetime.now()
        if self.state < 0:
            self.running = json.dumps({})
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
        self.running = json.dumps(running)
        self.save()
        
    def get_running(self):
        if self.running is not None:
            return json.loads(self.running)
        else:
            return {}

#===============================================================================#

class User(models.Model):
    name = models.CharField(max_length=60, db_index=True)

    state = models.IntegerField(default=1)
    class Meta:
        db_table = u'users'

    @property
    def accounts(self):
        return list(self.account_set.all())

    def __str__(self):
        return self.name

    @property
    def active(self):
        if self.state < 1:
            return False
        else:
            return True

#===============================================================================#

class Account(models.Model):
    user = models.ForeignKey(User)
    host = models.ForeignKey(Host)
    username = models.CharField(max_length=20)
    run_path = models.CharField(max_length=120)

    state = models.IntegerField(default=1)
    class Meta:
        db_table = 'accounts'

    def __str__(self):
        return '{user}@{host}'.format(user=self.user.name, 
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
        self.execute('mkdir %s &> /dev/null' % run_path, verbosity=verbosity)
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

    def execute(self, command='exit 0', verbosity=0):
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
        if stderr:
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
                stdout = subprocess.Popen('rm -f {path}/* &> /dev/null'.format(
                    path=destination)).communicate()[0]
            else:
                stdout = self.execute('rm -f {path}/* &> /dev/null'.format(
                path=destination))
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
                rmcmd = 'rm -rf {path} &> /dev/null'.format(path=os.path.abspath(folder))
            else:
                rmcmd = 'rm -f {path}/{file} &> /dev/null'.format(file=file,
                        path=os.path.abspath(folder))
            if verbosity > 0:
                print 'wiping source: ', rmcmd
            stdout = fr.execute(rmcmd)
            if verbosity > 0:
                print 'output:', stdout

#===============================================================================#

class Allocation(models.Model):
    name = models.CharField(max_length=50, db_index=True)
    key = models.CharField(max_length=100, default='')

    host = models.ForeignKey(Host, null=True)
    users = models.ManyToManyField(User, null=True)
    state = models.IntegerField(default=1)
    
    class Meta:
        db_table = u'allocations'

    def __str__(self):
        return self.name

    @property
    def active(self):
        if self.state < 1:
            return False
        elif not self.host.active:
            return False
        else:
            return True

    def get_random_user(self):
        return random.choice(self.users.filter(state=1))

    def get_random_account(self, project=None):
        users = self.users.filter(state=1)
        if not project is None:
            users = users.filter(name__in=project.users.all())
        user = random.choice(users)
        return user.account_set.get(host=self.host)

#===============================================================================#

class Project(models.Model):
    name = models.CharField(max_length=60)
    priority = models.IntegerField(default=0)

    users = models.ManyToManyField(User)
    allocations = models.ManyToManyField(Allocation)
    state = models.IntegerField(default=1)
    class Meta:
        db_table = u'projects'

    def __str__(self):
        return self.name

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
