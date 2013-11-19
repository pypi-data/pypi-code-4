import logging
import sys
import fnmatch

__author__ = 'alexey.grachev'
forwardSeconds = 300
backwardSeconds = 300
maxStatesSeq = 100
archiverPackCommandLine = '7z a -mx9 {archiveName} {dirToArchive}'
customWordsSearch = ['BugSl', 'Log.dll version']
messageStartPos = 49

import os.path
import collections
from datetime import datetime, timedelta

class AbstractLineProcessor:
    def process(self, line):
        pass

class BugslLineProcessor(AbstractLineProcessor):
    def __init__(self, outputDir, searchPatterns):
        self.outputFile = None
        self.faultBlockStart = None
        self.currentCrashThreadId = None
        self.amMap = dict()
        self.outputDir = outputDir
        self.searchPatterns = searchPatterns

    def begin(self, fileName, file):
        self.outputFile = open(os.path.join(self.outputDir, 'crash_' + fileName), "w")

    def process(self, line):
        threadId = line[14:24]

        item = self.amMap.get(threadId)
        if item is None:
            (states, events) = (collections.deque(maxlen=maxStatesSeq), collections.deque(maxlen=maxStatesSeq))
            self.amMap[threadId] = (states, events)
        else:
            (states, events) = item

        if len(line) >messageStartPos and line[messageStartPos] == '-':
            events.clear()
            if 'CStIdle' in line:
                states.clear()
                events.clear()
                if threadId == self.currentCrashThreadId:  #forget about crash if  CStIdle
                    self.currentCrashThreadId = None
            states.append(line)
        events.append(line)

        needToWrite = False
        if 'BugSl' in line:
            if not self.currentCrashThreadId:
                logging.info('Found crash at {}'.format(line[1:13]))
                self.outputFile.write('[----------------------------------------------Hooray!!! We got crash :\'(----------------------------------------------]\n')

                self.currentCrashThreadId = threadId
                logging.debug("Dumping states: {0} ".format(len(states)))
                self.outputFile.write('[Last call states for thread {}]\n'.format(threadId))
                for state in states:
                    self.outputFile.write(state)

                logging.debug("Dumping events: {0}".format(len(events)))
                self.outputFile.write('[Last call last state events for thread {}]\n'.format(threadId))
                for event in events:
                    self.outputFile.write(event)

                states.clear()
                events.clear()
                return #to avoid duplication of 'FAULT: An Exception occured'
            needToWrite = True

        if self.currentCrashThreadId and self.currentCrashThreadId in line:
            needToWrite = True

        # write process start/stop events, reset current crash
        if 'LogInfo' in line:
            self.currentCrashThreadId = None  #forget about crash
            needToWrite = True

        if needToWrite:
            self.outputFile.write(line)

    def end(self):
        self.outputFile.close()
        self.outputFile = None

class DateRangeLineProcessor(AbstractLineProcessor):
    def __init__(self, outputDir, startTime, endTime):
        self.outputDir = outputDir
        self.startTime = startTime
        self.endTime = endTime

    def begin(self, fileName, file):
        self.file = open(os.path.join(self.outputDir, 'cut_' + fileName), "w")

    def process(self, line):
        curTime = line[1:len(self.startTime) + 1]
        if self.startTime <= curTime <= self.endTime:
            self.file.write(line)

    def end(self):
        self.file.close()
        self.file = None

class ArchiveProcessor:
    def __init__(self):
        self.processors = []

    def attachProcessor(self, processor):
        self.processors.append(processor)

    def processFile(self, file):
        logging.info(str.format("Processing {0}", file.name))
        for line in file:
            for processor in self.processors:
                processor.process(line)

    def process(self, path, fileName):
        logging.info("Analyzing logs from: {0}".format(path))
        with open(os.path.join(path, fileName), "r") as file:
            for processor in self.processors: processor.begin(fileName, file)
            self.processFile(file)
            for processor in self.processors: processor.end()

class Analyzer:
    def __init__(self):
        self.forwardSeconds = forwardSeconds
        self.backwardSeconds = backwardSeconds

    def prepareTimes(self, eventTimeStr):
        eventDateTime = datetime.strptime(eventTimeStr, "%H:%M:%S")
        startTimeStr = (eventDateTime - timedelta(seconds=backwardSeconds)).strftime("%H:%M:%S")
        endTimeStr = (eventDateTime + timedelta(seconds=backwardSeconds)).strftime("%H:%M:%S")
        logging.debug("Start time\tEvent Time\tEndTime")
        logging.debug('{0}\t{1}\t{2}'.format(startTimeStr, eventTimeStr, endTimeStr))
        return startTimeStr, endTimeStr

    def analyze(self, issue, arguments):
        try:
            logging.info("------------------------------Analyzing")
            issue.setStatus('Analyzing')
            if issue.unpacked() is None:
                logging.error('No dir with unpacked logs')
                logging.debug('Traceback', exc_info=sys.exc_info())
                raise Exception('No dir with unpacked logs')

            dest = os.path.join(arguments.outputDir, issue.dest())
            for name in os.listdir(issue.unpacked()):
                if any(fnmatch.fnmatch(name, filter) for filter in arguments.logFilesFilter):
                    processor = ArchiveProcessor()
                    processor.attachProcessor(BugslLineProcessor(dest, customWordsSearch))
                    if issue.time():
                        (startTime, endTime) = self.prepareTimes(issue.time())
                        processor.attachProcessor(DateRangeLineProcessor(dest, startTime, endTime))
                    processor.process(issue.unpacked(), name)
                    issue.setStatus("Analyzed")
                else:
                    logging.debug('Skipping {0}'.format(name))
        except Exception as e:
            logging.error(str(e))
            logging.debug('Traceback', exc_info=sys.exc_info())
            raise Exception('Failed to analyze')



