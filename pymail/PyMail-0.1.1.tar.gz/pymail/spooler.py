'''
This module contains the Job class
'''

import configuration
import tempfile
import sink
from debug import D
import os
import re
import sys
import time
import eventlet

#: Default spool directory
SPOOLDIR = '/var/spool/pymail'

class Spooler(object):
    '''
    The spooler mechanism
    '''

    #: Pause (seconds) to wait between periodical scans
    CRONPAUSE = 10
    #: Registry of mail sinks
    sinks = {
        'smtp': sink.Smtp,
        'maildir': sink.MailDir
    }

    def __init__(self, config):
        '''
        Create Spooler object

        :param config: server configuration
        '''
        #: Configuration
        self.config = config
        #: Spool directory (from configuration)
        self.spoolDir = self.config('spooldir', SPOOLDIR)
        #: Flag when scan is running
        self.scanRunning = False
        #: Destination table
        self.destinations = []
        if config.has('destinations'):
            for d in config.destinations._.itervalues():
                d2 = d.copy()
                d2.setdefault('domain', '.*')
                d2.setdefault('priority', sys.maxint)
                d2['domainRe'] = re.compile(d2['domain'])
                self.destinations.append(configuration.DictMapper(d2))
            self.destinations.sort(lambda d, e: cmp(d._['priority'], e._['priority']))
        try:
            os.makedirs(self.spoolDir, 0700)
        except:
            pass

    def cron(self):
        '''
        Periodically start scan
        '''
        D('CRON STARTED')
        while True:
            self.scan()
            eventlet.sleep(self.CRONPAUSE)

    def scan(self):
        '''
        Scan spool directory for mail to process
        '''
        if not self.scanRunning:
            self.scanRunning = True
            for f in sorted(os.listdir(self.spoolDir), reverse=True):
                if f[-4:] == '.job':
                    self.process(os.path.join(self.spoolDir, f))
            self.scanRunning = False

    def process(self, fileName):
        '''
        Process job
        '''
        mailFrom = None
        rcptTo = []
        # Read job file
        for line in file(fileName):
            line = line.rstrip()
            if line[:5] == 'from:':
                mailFrom = line[5:]
            elif line[:3] == 'to:':
                rcptTo.append(line[3:])
            elif line[:5] == 'data:':
                dataFilename = line[5:]
            else:
                D('WARNING: Invalid job entry: ', line)
            eventlet.sleep(0)
        # Deliver mail to all destinations
        for r in rcptTo:
            at = r.find('@')
            if at < 0:
                rdomain = self.config.domain
            else:
                rdomain = r[at + 1:]
            # Find destination domain
            for d in self.destinations:
                if d.domainRe.match(rdomain):
                    break
            else:
                #TODO: Return error mail
                return
            mailSink = self.sinks[d.type](d)
            mailSink.send(mailFrom, r, dataFilename)
            eventlet.sleep(0)
        os.remove(fileName)
        eventlet.sleep(0)
        os.remove(dataFilename)
        eventlet.sleep(0)

class Job(object):
    '''
    Spool job
    '''

    def __init__(self, config):
        '''
        Create Job object
        '''
        #: ``spooler`` section of the configuration
        self.config = config
        mtime = '%09x-' % time.mktime(time.gmtime())
        #: Data file
        self.dataFile = tempfile.NamedTemporaryFile(
            mode='w+', suffix='.data', prefix=mtime, dir=self.config('spooldir', SPOOLDIR), delete=False
        )
        #: Job file
        self.jobFile = tempfile.NamedTemporaryFile(
            mode='w+', suffix='.job.tmp', prefix=mtime, dir=self.config('spooldir', SPOOLDIR), delete=False
        )
        self.jobFile.write('data:%s\n' % self.dataFile.name)

    def __del__(self):
        '''
        Destroy Job object
        '''
        if self.dataFile:
            os.remove(self.dataFile.name)
            self.dataFile = None
        if self.jobFile:
            os.remove(self.jobFile.name)
            D('JOB DESTROYED: ', self.jobFile.get('name', '(no file)'))
            self.jobFile = None

    def close(self):
        '''
        Close job

        Closes (and commits) a job. A job which is not closed will not be permanent.
        '''
        if self.dataFile:
            self.dataFile.close()
            self.dataFile = None
        if self.jobFile:
            self.jobFile.close()
            os.rename(self.jobFile.name, self.jobFile.name[:-4])
            self.jobFile = None

    def setSource(self, mailFrom):
        '''
        Set mail source

        :param string mailFrom: mail source

        Writes the mail source address to the job file.
        '''
        self.jobFile.write('from:%s\n' % mailFrom)

    def addDestination(self, rcptTo):
        '''
        Spool mail

        :param string rcptTo: mail destination

        Writes the mail destination to the job file.
        '''
        self.jobFile.write('to:%s\n' % rcptTo)

    def addData(self, line):
        '''
        Spool mail

        :param string line:

        Writes the data line to the data file.
        '''
        self.dataFile.write(line + '\n')
