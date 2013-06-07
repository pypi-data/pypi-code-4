#!/usr/bin/python

""" Creates a threadable worker object for looking up ORB records. """

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2011, Projex Software'
__license__         = 'LGPL'

# maintanence information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

import logging
import time

from projexui.qt import Signal
from projexui.qt.QtCore import QObject

logger = logging.getLogger(__name__)

try:
    from orb import Orb, RecordSet
except ImportError:
    RecordSet = None

class XOrbLookupWorker(QObject):
    loadingStarted = Signal()
    loadedGroup = Signal(str, object)
    loadedRecord = Signal(object)
    loadedRecords = Signal(object)
    loadingFinished = Signal()
    progressMessageLogged = Signal(str)
    progressTotalChanged = Signal(int)
    progressIncremented = Signal()
    
    def __init__(self, *args):
        super(XOrbLookupWorker, self).__init__(*args)
        
        # define custom properties
        self._cancelled = False
        self._running   = False
        self._batchSize = 100
        self._batched   = True
    
    def batchSize(self):
        """
        Returns the page size for this loader.
        
        :return     <int>
        """
        return self._batchSize
    
    def cancel(self):
        """
        Cancels the current lookup.
        """
        if self._running:
            self._cancelled = True
            self.loadingFinished.emit()
    
    def isBatched(self):
        """
        Returns whether or not this worker is processing in batches.  You should
        enable this if you are not working with paged results, and disable
        if you are working with paged results.
        
        :return     <bool>
        """
        return self._batched
    
    def isRunning(self):
        """
        Returns whether or not this worker is currently running.
        """
        return self._running
    
    def loadRecords(self, records):
        """
        Loads the record set for this instance.
        
        :param      records | <orb.RecordSet> || <list>
        """
        if self._running:
            return
        
        self._cancelled = False
        self._running = True
        
        self.loadingStarted.emit()
        
        # make sure the orb module is loaded, or there is really no point
        if RecordSet is None:
            logger.error('No RecordSet class was found.  Orb was not loaded.')
        
        # don't bother processing non-records
        elif not records:
            time.sleep(0.25)
        
        # process non-record sets
        elif not RecordSet.typecheck(records):
            records = sorted(list(records))
            page_size = self.batchSize()
            for i in range(0, len(records), page_size):
                batch = records[i:i+page_size]
                for record in batch:
                    if self._cancelled:
                        break
                    
                    # make sure everything is loaded for string conversion
                    record.recordValues(autoInflate=True)
                    self.loadedRecord.emit(record)
                
                self.loadedRecords.emit(batch)
        
        # lookup a group of results
        elif records.groupBy():
            for key, records in records.grouped().items():
                if self._cancelled:
                    break
                
                self.loadedGroup.emit(str(key), records)
        
        # lookup a list of results, in batched mode
        elif self.isBatched():
            total = len(records)
            batchSize = self.batchSize()
            
            count = 0
            for page in records.paged(self.batchSize()):
                if self._cancelled:
                    break
                
                batch = []
                if not records.order():
                    page_records = sorted(list(page))
                else:
                    page_records = list(page)
                
                for record in page_records:
                    if not count:
                        self.progressTotalChanged.emit(total)
                    
                    msg = 'Loading record %i of %i' % (count, total)
                    self.progressMessageLogged.emit(msg)
                    self.progressIncremented.emit()
                    
                    if self._cancelled:
                        break
                    
                    # make sure everything is loaded for string conversion
                    record.recordValues(autoInflate=True)
                    self.loadedRecord.emit(record)
                    batch.append(record)
                    
                    count += 1
                    if count == total:
                        break
                
                self.loadedRecords.emit(batch)
        
        # lookup a list of results, not in batched mode
        else:
            total = len(records)
            batchSize = self.batchSize()
            records = list(records)
            self.progressTotalChanged.emit(total)
            
            for count, record in enumerate(records):
                msg = 'Loading record %i of %i' % (count, total)
                self.progressMessageLogged.emit(msg)
                self.progressIncremented.emit()
                
                if self._cancelled:
                    break
                
                # make sure everything is loaded for string conversion
                record.recordValues(autoInflate=True)
                self.loadedRecord.emit(record)
            
            self.loadedRecords.emit(records)
        
        self._running = False
        self.loadingFinished.emit()

    def setBatchSize(self, batchSize):
        """
        Sets the page size for this loader.
        
        :param     batchSize | <int>
        """
        self._batchSize = batchSize
    
    def setBatched(self, state):
        """
        Sets the maximum number of records to extract.  This is used in
        conjunction with paging.
        
        :param      maximum | <int>
        """
        self._batched = state