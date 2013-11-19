import os
import sys


__author__ = 'alexey.grachev'
import logging
import tables

class Issue:
    def __init__(self, key=None, machine=None, service=None, eventDate=None, eventTime=None, archive=None):
        self._key = key
        self._machine = machine
        self._service = service
        self._date = eventDate
        self._time = eventTime
        self._archive = archive
        self._error = 'Ready'
        self._unpacked = None

    def key(self):
        return self._key

    def setKey(self, key):
        self._key = key

    def machine(self):
        return self._machine

    def setMachine(self, machine):
        self._machine = machine

    def service(self):
        return self._service

    def setService(self, service):
        self.service = service

    def date(self):
        return self._date

    def setDate(self, date):
        self._date = date

    def time(self):
        return self._time

    def setTime(self, time):
        self._time = time

    def status(self):
        return self._error

    def setStatus(self, error):
        self._error = error

    def archive(self):
        return self._archive

    def setArchive(self, archive):
        self._archive = archive

    def unpacked(self):
        return self._unpacked

    def setUnpacked(self, unpacked):
        self._unpacked = unpacked

    def dest(self):
        if self.key():
            return self.key()
        if self.machine() and self.date():
            return 'logs_{0}_{1}.zip'.format(self.date(), self.machine())
        if self.archive():
            return os.path.splitext(os.path.basename(self.archive()))[0]
        if self.unpacked():
            return os.path.basename(self.unpacked())
        return '\\'

    def report(self):
        return [self.key(), self.machine(), self.service(), self.date(), self.time(), self.archive(), self.unpacked(), self.dest(), self.status()]

    def __str__(self):
        return 'Issue[{0} {1} {2} {3} {4} {5} {6} {7} {8}]'.format(
            self.key(), self.machine(), self.service(), self.date(), self.time(), self.archive(), self.unpacked(), self.dest(), self.status())


class Issues:
    def __init__(self):
        self.issues = list()
        self.emptyFunc = lambda self: None
        self._downloaderFunc = self.emptyFunc
        self._unpackerFunc = self.emptyFunc
        self._analyzerFunc = self.emptyFunc

    def __iter__(self):
        for issue in self.issues:
            yield issue

    def setDownloader(self, func):
        self._downloaderFunc = func

    def setUnpacker(self, func):
        self._unpackerFunc = func

    def setAnalyser(self, func):
        self._analyzerFunc = func

    def appender(self):
        return lambda key, machine, service, eventDate, eventTime: self.issues.append(Issue(key=key, machine=machine, service=service, eventDate=eventDate, eventTime=eventTime))

    def getList(self):
        return self.issues

    def append(self, issue):
        self.issues.append(issue)

    def extend(self, issues):
        self.issues.extend(issues)

    def appendKeys(self, keys):
        for key in keys:
            self.issues.append(Issue(key=key))

    def appendAnalyze(self, analyze):
        for item in analyze:
            self.issues.append(Issue(archive=item))

    def process(self, arguments):
        for issue in self.issues:
            try:
                if self._downloaderFunc == self.emptyFunc and self._analyzerFunc == self.emptyFunc:
                    return

                logging.info(self.report())
                logging.info('------------------------------Processing: {0}'.format(issue))
                outputDir = os.path.join(arguments.outputDir, issue.dest())
                logging.info('Output to: {0}'.format(outputDir))
                os.makedirs(outputDir)

                self._downloaderFunc(issue)
                if issue.archive():
                    self._unpackerFunc(issue)

                self._analyzerFunc(issue)
                issue.setStatus('Done')
            except Exception as e:
                logging.error(str(e))
                issue.setStatus(str(e))
                logging.debug('Traceback', exc_info=sys.exc_info())

    def report(self):
        try:
            table = []
            table.append(['Issue', 'Machine', 'Service', 'Date', 'Time', 'Archive', 'Unpacked', 'Dest', 'Status'])
            for issue in self.issues:
                table.append(issue.report())
            return "Current issues:\n" + tables.print_table(table)[:-1]
        except Exception as e:
            logging.error("Fatal error: " + str(e))
            logging.debug('Traceback', exc_info=sys.exc_info())


