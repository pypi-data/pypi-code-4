'''
The Spooler class in this module takes care of processing e-mail in the spool database
'''
from . import configuration, sink
from pymail import client
import cPickle
import datetime
import email
import eventlet
import logging
import os
import re
import sqlite3
import sys
import uuid

#: Blocksize for message parts in spool database
BLOCKSIZE = 65536
#: Default spool file
DEFAULT_SPOOLFILE = '/var/spool/pymail'
#: Default retry plan
DEFAULT_RETRY_PLAN = ['4*30m', '22*1h', '4*1d']
#: Spool SQL schema
SQL_SCHEMA = '''
Create Table Job (
    MessageId    Varchar(64) Not Null Unique,
    Source       Varchar(256) Not Null,
    Headers      Blob Not Null,
    Spooled      Datetime Not Null
);
Create Table JobDestination (
    JobId        Integer Not Null,
    Destination  Varchar(256) Not Null,
    Tries        Integer Not Null,
    NextTry      DateTime Not Null,
    Foreign Key (JobId) References Job(Oid) On Delete Cascade
);
Create Index JobDestination_JobId On JobDestination (JobId);
Create Table Body (
    JobId        Integer Not Null,
    Part         Blob Not Null,
    Foreign Key (JobId) References Job(Oid) On Delete Cascade
);
Create Index Body_JobId On Body (JobId);
'''
ERROR_TEMPLATE = '''
Delivery to the following recipient failed permanently:

%(destination)s

Technical details of permanent failure: 
%(address)s tried to deliver your message, but it was rejected by %(host)s.

The error that the other server returned was:
%(message)
'''

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
    retryPlanElementRe = re.compile(r'^(?:(\d+)\*)?(?:(\d+)([smhdwMy]?))$')
    timeMultiplier = {'': 60, 's': 1, 'm': 60, 'h': 3600, 'd':86400, 'w': 604800, 'M': 18144000, 'y': 31536000}

    def __init__(self, config):
        '''
        Create Spooler object

        :param config: server configuration
        '''
        #: Logger
        self.log = logging.getLogger('pymail.spooler.Spooler')
        #: Configuration
        self.config = config
        #: Spool directory (from configuration)
        self.spoolPath = self.config('spoolfile', DEFAULT_SPOOLFILE)
        #: Retry plan
        self.retryPlan = []
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
        newSpooleFile = not os.path.exists(self.spoolPath)
        self.spoolFile = sqlite3.connect(self.spoolPath, detect_types=sqlite3.PARSE_COLNAMES)
        if newSpooleFile:
            self.spoolFile.executescript(SQL_SCHEMA)
        self._setupRetryPlan()

    def _setupRetryPlan(self):
        '''
        Convert retry plan from config format to list of seconds
        '''
        for e in self.config('retries', DEFAULT_RETRY_PLAN):
            match = self.retryPlanElementRe.match(str(e)) # e could by integer
            assert match, 'retries elements must be of format [n*]tu: ' + e
            time = int(match.group(2)) * self.timeMultiplier[match.group(3)]
            repeat = int(match.group(1) or '1')
            self.retryPlan.extend(repeat * [time])

    def cron(self):
        '''
        Periodically start scan
        '''
        self.log.info('Cron started')
        while True:
            self.scan()
            eventlet.sleep(self.CRONPAUSE)

    def scan(self):
        '''
        Scan spool directory for mail to process
        '''
        if not self.scanRunning:
            self.scanRunning = True
            for job in self.spoolFile.execute(
                '''
                Select Job.Oid, MessageId, Source, Headers, Spooled As "Spooled[timestamp]"
                From Job
                Left Join JobDestination On JobId == Job.Oid
                '''
            ):
                self.process(*job) # NOTE: fields from SQL query make up function call!
            self.scanRunning = False


    def _deleteJobDestination(self, oid):
        '''
        Delete JobDestination record

        :param oid:
        :return: cursor
        '''
        return self.spoolFile.execute('Delete From JobDestination Where JobId = ?', (oid, ))

    def bounce(self, oid, error, sink):
        '''
        Bounce message and remove

        :param int oid:
        :param string error:
        :param sink.Sink sink:
        '''
        self._deleteJobDestination(oid)
        self.returnError(sink, str(error))

    def process(self, jobId, messageId, mailSource, headers, spooled):
        '''
        Process job

        :param int jobId:
        :param string messageId:
        :param string mailSource:
        :param string mailDestination:
        :param string headers: pickled dict
        :param datetime.dateime spooled: time of spooling
        :param int tries:
        '''
        self.log.info('Processing mail %s', messageId)
        headers = cPickle.loads(str(headers))
        # Set up the list of mail sinks to which the data is pushed in parallel
        mailSinks = {}
        mailDestinations = self.spoolFile.execute(
            '''
            Select Oid, Destination From JobDestination Where JobId = ? And NextTry <= DateTime('Now', 'Localtime')
            ''',
            (jobId,)
        )
        for oid, destination in mailDestinations:
            # Extract domain from destination address
            at = destination.find('@')
            if at < 0:
                rdomain = self.config.domain
            else:
                rdomain = destination[at + 1:]
            # Find destination domain in config
            try:
                dest = next(d for d in self.destinations if d.domainRe.match(rdomain))
            except StopIteration:
                # TODO: Return error mail
                self.log.error('No mailDestinations found for destination %s of %s', destination, messageId)
                continue
            mailSink = self.sinks[dest.type](self.config, dest, messageId, mailSource, destination, headers)
            try:
                mailSink.open()
            except client.TemporaryError as e:
                # Temporary errors mean we can retry later
                self.log.exception(e)
                mailSinks[oid] = [mailSink, destination, e]
            except:
                # All other errors are fatal
                self.log.exception(sys.exc_info()[1])
                self.bounce(oid, sys.exc_info()[1], mailSink)
            else:
                mailSinks[oid] = [mailSink, destination, None]
            eventlet.sleep()
        # Send data to all sinks
        length = 0
        if len(mailSinks.items()):
            self.log.debug('Start transferring DATA for %s to %s', messageId, dest)
            for (block,) in self.spoolFile.execute('Select Part From Body Where JobId = ?', (jobId,)):
                for oid, (s, d, e) in mailSinks.items():
                    try:
                        if not e: s.sendBodyBlock(str(block))
                    except:
                        self.log.exception('From sendBodyBlock')
                        mailSinks[oid][2] = sys.exc_info()[1]
                    length += len(block)
                    eventlet.sleep()
            self.log.info('Sent %d bytes to %s for %s', length, destination, messageId)
        # Close all sinks
        for oid, (s, d, e) in mailSinks.items():
            try:
                if not e:
                    self.log.debug('Closing connection to %s of %s', d, messageId)
                    s.close()
                    self._deleteJobDestination(oid)
            except:
                self.log.exception('Trying to close destination %s of message %s (oid=%d)', d, messageId, oid)
                mailSinks[oid][2] = sys.exc_info()[1]
            eventlet.sleep()
        # Reschedule destinations with errors
        for oid, (s, d, e) in mailSinks.items():
            if e:
                now = (datetime.datetime.now() - spooled).seconds
                acc = 0
                for i in self.retryPlan:
                    if acc > now: break
                    acc += i
                else:
                    self.log.error('No more retries for destination %s of %s', d, messageId)
                    self.bounce(oid, e, s)
                    continue
                new = spooled + datetime.timedelta(0, acc)
                self.spoolFile.execute(
                    'Update JobDestination Set NextTry = ? Where Oid = ?',
                    (new, oid)
                )
                self.log.info('Destination %s for message %s rescheduled to %s' % (d, messageId, new))
        # If all destinations are done remove job and body
        result = self.spoolFile.execute('Select Count(*) From JobDestination Where JobId = ?', (jobId,))
        destCount = result.fetchone()[0]
        if destCount < 1:
            self.log.info('Message %s completed' % messageId)
            self.spoolFile.execute('Delete From Job Where Oid = ?', (jobId,))
            self.spoolFile.execute('Delete From Body Where JobId = ?', (jobId,))
        self.spoolFile.commit()

    def returnError(self, sink, message):
        '''
        Return error mail to source

        :param sink.Sink sink:
        :param message: somthing that can be converted to a string
        '''
        job = Job(self.spoolFile, '', uuid.uuid4().hex)
        job.addDestination(sink.source)
        job.addHeader('Return-Path: <>')
        job.addHeader('From: mailer-daemon@%s' % sink.sconfig.address)
        job.addHeader('To: %s' % sink.source)
        job.addHeader('Subject: Delivery Status Notification (Failure)')
        job.addHeader('Date: %s' % email.Utils.formatdate(localtime=True))
        data = dict(
            message=str(message),
            address=sink.sconfig.address,
            destination=sink.destination,
            host=sink.clientSession.host
        )
        text = ''.join(line + '\r\n' for line in (ERROR_TEMPLATE.strip() % data).splitlines())
        job.addBody(text)
        job.commit()

class Job(object):
    '''
    '''

    def __init__(self, spoolFile, source, messageId):
        '''
        Create spool job

        :param spoolFile: SQLite database connection
        :param source:
        :param messageId:
        '''
        #: Database
        self.spoolFile = spoolFile
        #: Source mail address
        self.source = source
        #: Message ID
        self.messageId = messageId
        #: List of destinations
        self.destinations = []
        #: List of headers
        self.headers = []
        #: Row ID
        self.id = None
        #: Body buffer
        self.buffer = bytearray()

    def addDestination(self, destination):
        '''
        Add destination mail address

        :param destination:
        '''
        self.destinations.append(destination)

    def addHeader(self, text):
        '''
        Add mail message header

        :param text: header line; if indented, added to last header
        '''
        if text.startswith(' '):
            self.headers[-1] += text
        else:
            self.headers.append(text)

    def insertHeader(self, text):
        '''
        Insert mail message header in front of list

        :param text: header line; if indented, added to first header
        '''
        if text.startswith(' '):
            self.headers[0] += text
        else:
            self.headers.insert(0, text)

    def addBody(self, text):
        '''
        Add body text

        :param text:

        The first time `addBody` is called, the Job and JobDestinations rows are written, such that the row ID is known.
        '''
        assert self.destinations, 'No destinations have been added'
        assert self.headers, 'No headers have been added'
        if not self.id:
            cursor = self.spoolFile.execute(
                '''
                Insert Into Job (MessageId, Source, Headers, Spooled)
                Values (?, ?, ?, ?)
                ''', (
                    self.messageId,
                    self.source,
                    cPickle.dumps(self.headers),
                    datetime.datetime.now()
                )
            )
            self.id = cursor.lastrowid
            for r in self.destinations:
                self.spoolFile.execute(
                    '''
                    Insert Into JobDestination (JobId, Destination, Tries, NextTry)
                    Values (?, ?, ?, ?)
                    ''', (
                        self.id,
                        r,
                        0,
                        datetime.datetime.now()
                    )
                )
        self.buffer.extend(text)
        if len(self.buffer) > BLOCKSIZE:
            self.spoolFile.execute(
                'Insert Into Body (JobId, Part) Values (?, ?)',
                (
                    self.id,
                    str(self.buffer[:BLOCKSIZE])
                )
            )
            self.buffer = self.buffer[BLOCKSIZE:]

    def commit(self):
        if self.buffer:
            self.spoolFile.execute(
                'Insert Into Body (JobId, Part) Values (?, ?)',
                (
                    self.id,
                    str(self.buffer)
                )
            )
            self.buffer = bytearray()
        self.spoolFile.commit()

    def rollback(self):
        self.spoolFile.rollback()
