#!/usr/bin/python
#backup_rebuilder.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2013
#    Use of this software constitutes acceptance of the Terms of Use
#      http://datahaven.net/terms_of_use.html
#    All rights reserved.
#

import os
import sys
import time
import random


try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in backup_rebuilder.py')

from twisted.internet.defer import Deferred, maybeDeferred
from twisted.internet import threads


import lib.dhnio as dhnio
import lib.misc as misc
import lib.nameurl as nameurl
import lib.transport_control as transport_control
import lib.settings as settings
import lib.contacts as contacts
import lib.eccmap as eccmap
import lib.tmpfile as tmpfile
import lib.diskspace as diskspace
import lib.packetid as packetid
from lib.automat import Automat


import fire_hire
import backup_monitor
import block_rebuilder
import lib.automats as automats

import backups
import raidread
import io_throttle
import backup_db

_BackupRebuilder = None
_StoppedFlag = True
_BackupIDsQueue = []  
_BlockRebuildersQueue = []

#------------------------------------------------------------------------------ 

def A(event=None, arg=None):
    global _BackupRebuilder
    if _BackupRebuilder is None:
        _BackupRebuilder = BackupRebuilder('backup_rebuilder', 'STOPPED', 12)
    if event is not None:
        _BackupRebuilder.automat(event, arg)
    return _BackupRebuilder


class BackupRebuilder(Automat):
    timers = {'timer-1sec':     (1,     ['NEXT_BLOCK', 'NEXT_BACKUP']),
              'timer-01sec':    (0.1,   ['NEXT_BLOCK']), }
    
    def init(self):
        self.currentBackupID = None             # currently working on this backup
        self.currentBlockNumber = -1            # currently working on this block
        self.workingBlocksQueue = []            # list of missing blocks we work on for current backup 
        self.maxBlockRebuilderQueueLength = 8   # TODO - need to sort out what is an appropriate length

    def state_changed(self, oldstate, newstate):
        # automats.set_global_state('REBUILD ' + newstate)
        backup_monitor.A('backup_rebuilder.state', newstate)
        
    def A(self, event, arg):
        #---STOPPED---
        if self.state is 'STOPPED':
            if event == 'start' :
                self.state = 'NEXT_BACKUP'
                self.doClearStoppedFlag(arg)
            elif event == 'init' :
                pass
        #---NEXT_BACKUP---
        elif self.state is 'NEXT_BACKUP':
            if event == 'timer-1sec' and not self.isStopped(arg) and self.isMoreBackups(arg) :
                self.state = 'NEXT_BLOCK'
                self.doTakeNextBackup(arg)
                self.doTakeNextBlock(arg)
            elif event == 'timer-1sec' and not self.isMoreBackups(arg) and not self.isStopped(arg) :
                self.state = 'DONE'
            elif event == 'timer-1sec' and self.isStopped(arg) :
                self.state = 'STOPPED'
        #---NEXT_BLOCK---
        elif self.state is 'NEXT_BLOCK':
            if event == 'timer-01sec' and not self.isStopped(arg) and not self.isMoreBlocks(arg) and self.isMoreBackups(arg) :
                self.state = 'NEXT_BACKUP'
            elif event == 'timer-01sec' and ( ( not self.isMoreBackups(arg) and not self.isMoreBlocks(arg) ) or self.isFailedSuppliers(arg) ) :
                self.state = 'DONE'
            elif event == 'timer-1sec' and self.isStopped(arg) :
                self.state = 'STOPPED'
            elif ( event == 'timer-01sec' or event == 'block-done' ) and not self.isStopped(arg) and self.isMoreBlocks(arg) and not self.isFailedSuppliers(arg) and self.isSpaceForNewBlockRebuilder(arg) :
                self.state = 'REBUILDING'
                self.doRequestNeededPackets(arg)
                self.doStartNewBlockRebuilder(arg)
        #---REBUILDING---
        elif self.state is 'REBUILDING':
            if ( event == 'block_rebuilder.state' and arg in [ 'FINISHED' , 'STOPPED' , 'DONE' ] ) :
                self.state = 'NEXT_BLOCK'
                self.doTakeNextBlock(arg)
            elif ( event == 'block_rebuilder.state' and arg is 'TIMEOUT' ) :
                self.state = 'DONE'
        #---DONE---
        elif self.state is 'DONE':
            if event == 'start' :
                self.state = 'NEXT_BACKUP'
                self.doClearStoppedFlag(arg)

    def isStopped(self, arg):
        return ReadStoppedFlag() == True # :-)

    def isMoreBackups(self, arg):
        global _BackupIDsQueue
        return len(_BackupIDsQueue) > 0
    
    def isMoreBlocks(self, arg):
        # because started from 0,  -1 means not found 
        return self.currentBlockNumber > -1 
    
    def isSpaceForNewBlockRebuilder(self, arg):
        global _BlockRebuildersQueue
        return len(_BlockRebuildersQueue) < self.maxBlockRebuilderQueueLength

    def isFailedSuppliers(self, arg):
        # failed_suppliers = backups.GetFailedSuppliers()
        # dhnio.Dprint(6, 'backup_rebuilder.isFailedSuppliers return %s: %s' % (str(len(failed_suppliers) > 0), failed_suppliers))
        # return len(failed_suppliers) > 0
        return False

    def doTakeNextBackup(self, arg):
        global _BackupIDsQueue
        # take a first backup from queue to work on it
        backupID = _BackupIDsQueue.pop(0)
        # dhnio.Dprint(6, 'backup_rebuilder.doTakeNextBackup first backup in queue is %s' % backupID)
        # if remote data structure is not exist for this backup - create it
        # this mean this is only local backup!
        if not backups.remote_files().has_key(backupID):
            backups.remote_files()[backupID] = {}
            # we create empty remote info for every local block
            # range(0) should return []
            for blockNum in range(backups.local_max_block_numbers().get(backupID, -1) + 1):
                backups.remote_files()[backupID][blockNum] = {
                    'D': [0] * backups.suppliers_set().supplierCount,
                    'P': [0] * backups.suppliers_set().supplierCount }
        # clear blocks queue from previous iteration
        self.currentBlockNumber = -1
        # del self.workingBlocksQueue
        self.workingBlocksQueue = [] 
        # detect missing blocks from remote info
        self.workingBlocksQueue = backups.ScanMissingBlocks(backupID)
        # find the correct max block number for this backup
        # we can have remote and local files
        # will take biggest block number from both 
        backupMaxBlock = max(backups.remote_max_block_numbers().get(backupID, -1),
                             backups.local_max_block_numbers().get(backupID, -1))
        # now need to remember this biggest block number
        # remote info may have less blocks - need to create empty info for missing blocks
        for blockNum in range(backupMaxBlock + 1):
            if backups.remote_files()[backupID].has_key(blockNum):
                continue
            backups.remote_files()[backupID][blockNum] = {
                'D': [0] * backups.suppliers_set().supplierCount,
                'P': [0] * backups.suppliers_set().supplierCount }
        # really take next backup
        self.currentBackupID = backupID
        # clear sending queue, remove old packets for this backup, we will send them again
        io_throttle.DeleteBackupRequests(self.currentBackupID)
        # dhnio.Dprint(6, 'backup_rebuilder.doTakeNextBackup currentBackupID=%s workingBlocksQueue=%d' % (self.currentBackupID, len(self.workingBlocksQueue)))
       
    def doTakeNextBlock(self, arg):
        if len(self.workingBlocksQueue) > 0:
            # let's take last blocks first ... 
            # in such way we can propagate how big is the whole backup as soon as possible!
            # remote machine can multiply [file size] * [block number] 
            # and calculate the whole size to be received ... smart!
            # ... remote supplier should not use last file to calculate
            self.currentBlockNumber = self.workingBlocksQueue.pop()
            # self.currentBlockNumber = self.workingBlocksQueue.pop(0)
        else:
            self.currentBlockNumber = -1
        self.automat('block-done')

    def doStartNewBlockRebuilder(self, arg):
        br = block_rebuilder.BlockRebuilder(
            eccmap.Current(), #self.eccMap,
            self.currentBackupID,
            self.currentBlockNumber,
            backups.suppliers_set(),
            backups.GetRemoteDataArray(self.currentBackupID, self.currentBlockNumber),
            backups.GetRemoteParityArray(self.currentBackupID, self.currentBlockNumber),
            backups.GetLocalDataArray(self.currentBackupID, self.currentBlockNumber),
            backups.GetLocalParityArray(self.currentBackupID, self.currentBlockNumber),)
        AddBlockRebuilder(br)
        br.automat('start')

    def doRequestNeededPackets(self, arg):
        # here we want to request some packets before we start working on blocks one by one
        # this should increase the speed because we do not need to wait for every request
        supplierSet = backups.suppliers_set()
        availableSuppliers = supplierSet.GetActiveArray()
        # localMaxBlockNum = backups.local_max_block_numbers().get(self.currentBackupID, -1)
        # at the moment I do download everything I have available and needed
        for supplierNum in range(supplierSet.supplierCount):
            # if supplier is not alive - we can't request from him           
            if availableSuppliers[supplierNum] == 0:
                continue
            supplierID = supplierSet.suppliers[supplierNum]
            # we do requests in reverse order because we start rebuilding from the last block 
            for blockNum in range(self.currentBlockNumber, -1, -1):
                remoteData = backups.GetRemoteDataArray(self.currentBackupID, blockNum)
                remoteParity = backups.GetRemoteParityArray(self.currentBackupID, blockNum)
                localData = backups.GetLocalDataArray(self.currentBackupID, blockNum)
                localParity = backups.GetLocalParityArray(self.currentBackupID, blockNum)
                # if the remote Data exist and is available because supplier is on line,
                # but we do not have it on hand - do request  
                if remoteData[supplierNum] == 1 and localData[supplierNum] == 0:
                    PacketID = packetid.MakePacketID(self.currentBackupID, blockNum, supplierNum, 'Data') 
                    if not io_throttle.HasPacketInSendQueue(supplierID, PacketID):
                        io_throttle.QueueRequestFile(
                            self.FileReceived, 
                            misc.getLocalID(), 
                            PacketID, 
                            misc.getLocalID(), 
                            supplierID)
                # same for Parity
                if remoteParity[supplierNum] == 1 and localParity[supplierNum] == 0:
                    PacketID = packetid.MakePacketID(self.currentBackupID, blockNum, supplierNum, 'Parity') 
                    if not io_throttle.HasPacketInSendQueue(supplierID, PacketID):
                        io_throttle.QueueRequestFile(
                            self.FileReceived, 
                            misc.getLocalID(), 
                            PacketID, 
                            misc.getLocalID(), 
                            supplierID)

    def doClearStoppedFlag(self, arg):
        ClearStoppedFlag()

    def FileReceived(self, packet, state):
        if state in ['in queue', 'shutdown', 'exist']:
            return
        if state != 'received':
            dhnio.Dprint(4, "backup_rebuilder.FileReceived WARNING incorrect state [%s] for packet %s" % (str(state), str(packet)))
            return
        packetID = packet.PacketID
        filename = os.path.join(settings.getLocalBackupsDir(), packetID)
        if packet.Valid():
            # if we managed to rebuild a file 
            # before a request came in don't overwrite it
            if os.path.exists(filename):
                dhnio.Dprint(4, "backup_rebuilder.FileReceived WARNING rewriting existed file" + filename)
                try: 
                    os.remove(filename)
                except:
                    dhnio.DprintException()
            dhnio.WriteFile(filename, packet.Payload)
        else:
            # TODO 
            # if we didn't get a valid packet ... re-request it or delete it?
            dhnio.Dprint(2, "backup_rebuilder.FileReceived WARNING " + filename + " is not a valid packet, remove it now")
            try: 
                os.remove(filename)
            except:
                dhnio.DprintException()
        backups.LocalFileReport(packetID)
        
#------------------------------------------------------------------------------ 

def AddBackupsToWork(backupIDs):
    global _BackupIDsQueue 
    _BackupIDsQueue.extend(backupIDs)


def RemoveBackupToWork(backupID):
    global _BackupIDsQueue
    if backupID in _BackupIDsQueue:
        _BackupIDsQueue.remove(backupID)


def SetStoppedFlag():
    global _StoppedFlag
    _StoppedFlag = True
    
    
def ClearStoppedFlag():
    global _StoppedFlag
    _StoppedFlag = False
    

def ReadStoppedFlag():
    global _StoppedFlag
    return _StoppedFlag
    
    
def AddBlockRebuilder(obj):
    global _BlockRebuildersQueue
    dhnio.Dprint(10, 'backup_rebuilder.AddBlockRebuilder for %s-%s' % (obj.backupID, str(obj.blockNum)))
    _BlockRebuildersQueue.append(obj)
    

def RemoveBlockRebuilder(obj):
    global _BlockRebuildersQueue
    dhnio.Dprint(10, 'backup_rebuilder.RemoveBlockRebuilder for %s-%s' % (obj.backupID, str(obj.blockNum)))
    _BlockRebuildersQueue.remove(obj)


    
    

    
