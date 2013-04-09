#!/usr/bin/python
#io_throttle.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2013
#    Use of this software constitutes acceptance of the Terms of Use
#      http://datahaven.net/terms_of_use.html
#    All rights reserved.
#
#    When reconstructing a backup we don't want to take over everything
#    and make DHN unresponsive by requesting 1000's of files at once
#    and make it so no other packets can go out,
#    this just tries to limit how much we are sending out or receiving at any time
#    so that we still have control.
#    Before requesting another file or sending another one out
#    I check to see how much stuff I have waiting.  


import os
import sys
import time


try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in io_throttle.py')


import lib.transport_control as transport_control
import lib.dhnio as dhnio
import lib.settings as settings
import lib.dhnpacket as dhnpacket
import lib.commands as commands
import lib.misc as misc
import lib.tmpfile as tmpfile
import lib.nameurl as nameurl


import contact_status

_IO = None
_PacketReportCallbackFunc = None

#------------------------------------------------------------------------------ 

def io():
    global _IO
    if _IO is None:
        _IO = IOThrottle()
    return _IO

def init():
    dhnio.Dprint(4,"io_throttle.init")
    _throttle = io()
    transport_control.AddOutboxPacketStatusFunc(OutboxStatus)

def SetPacketReportCallbackFunc(func):
    global _PacketReportCallbackFunc
    _PacketReportCallbackFunc = func
    
def PacketReport(sendORrequest, supplier_idurl, packetID, result):
    global _PacketReportCallbackFunc
    if _PacketReportCallbackFunc is not None:
        _PacketReportCallbackFunc(sendORrequest, supplier_idurl, packetID, result)

#------------------------------------------------------------------------------ 

def QueueSendFile(fileName, packetID, remoteID, ownerID, callOnAck=None, callOnFail=None):
    return io().QueueSendFile(fileName, packetID, remoteID, ownerID, callOnAck, callOnFail)

def QueueRequestFile(callOnReceived, creatorID, packetID, ownerID, remoteID):
    return io().QueueRequestFile(callOnReceived, creatorID, packetID, ownerID, remoteID)

def DeleteBackupRequests(backupName):
    return io().DeleteBackupRequests(backupName)

def DeleteSuppliers(supplierIdentities):
    return io().DeleteSuppliers(supplierIdentities)

def OutboxStatus(workitem, proto, host, status, error, message):
    return io().OutboxStatus(workitem, proto, host, status, error, message)
    
def IsSendingQueueEmpty():
    return io().IsSendingQueueEmpty()

def HasPacketInSendQueue(supplierIDURL, packetID):
    return io().HasPacketInSendQueue(supplierIDURL, packetID)

def OkToSend(supplierIDURL):
    return io().OkToSend(supplierIDURL)

def OkToRequest(supplierIDURL):
    return io().OkToRequest(supplierIDURL)

def GetSendQueueLength(supplierIDURL):
    return io().GetSendQueueLength(supplierIDURL)

def GetRequestQueueLength(supplierIDURL):
    return io().GetRequestQueueLength(supplierIDURL)

#------------------------------------------------------------------------------ 

class FileToRequest:
    def __init__(self, callOnReceived, creatorID, packetID, ownerID, remoteID):
        self.callOnReceived = []
        self.callOnReceived.append(callOnReceived)
        self.creatorID = creatorID
        self.packetID = packetID
        self.ownerID = ownerID
        self.remoteID = remoteID
        self.backupID = packetID[0:packetID.find("-")]
        self.requestTime = None
        self.fileReceivedTime = None
        self.requestTimeout = max(30, 2*int(settings.PacketSizeTarget()/settings.SendingSpeedLimit()))
        self.result = ''
        PacketReport('request', self.remoteID, self.packetID, 'init')
    
    def __del__(self):
        PacketReport('request', self.remoteID, self.packetID, self.result)

#------------------------------------------------------------------------------ 

class FileToSend:
    def __init__(self, fileName, packetID, remoteID, ownerID, callOnAck=None, callOnFail=None):
        self.fileName = fileName
        try:
            self.fileSize = os.path.getsize(os.path.abspath(fileName))
        except:
            dhnio.DprintException()
            self.fileSize = 0
        self.packetID = packetID
        self.remoteID = remoteID
        self.ownerID = ownerID
        self.callOnAck = callOnAck
        self.callOnFail = callOnFail
        self.sendTime = None
        self.ackTime = None
        self.sendTimeout = max( int(self.fileSize/settings.SendingSpeedLimit()), 60 )
        self.result = ''
        PacketReport('send', self.remoteID, self.packetID, 'init')
        
    def __del__(self):
        PacketReport('send', self.remoteID, self.packetID, self.result)

#------------------------------------------------------------------------------ 

#TODO I'm not removing items from the dict's at the moment
class SupplierQueue:
    def __init__(self, supplierIdentity, creatorID):
        self.creatorID = creatorID
        self.remoteID = supplierIdentity
        self.remoteName = nameurl.GetName(self.remoteID)

        # all sends we'll hold on to, only several will be active, 
        # but will hold onto the next ones to be sent
        # self.fileSendQueueMaxLength = 32
        # active files 
        self.fileSendMaxLength = 1 # 1 mean sending files one by one! 
        # an array of packetId, preserving first in first out, 
        # of which the first maxLength are the "active" sends      
        self.fileSendQueue = []
        # dictionary of FileToSend's using packetId as index, 
        # hold onto stuff sent and acked for some period as a history?         
        self.fileSendDict = {}          

        # all requests we'll hold on to, 
        # only several will be active, but will hold onto the next ones to be sent
        # self.fileRequestQueueMaxLength = 6
        # active requests 
        self.fileRequestMaxLength = 1 # do requests one by one   
        # an arry of PacketIDs, preserving first in first out
        self.fileRequestQueue = []      
        # FileToRequest's, indexed by PacketIDs
        self.fileRequestDict = {}       

        self.dprintAdjust = 0
        self.shutdown = False

        self.ackedCount = 0
        self.failedCount = 0
        
        self.sendFailedPacketIDs = []
        
        self.sendTask = None
        self.sendTaskDelay = 0.1
        self.requestTask = None
        self.requestTaskDelay = 0.1


    def RemoveSupplierWork(self): 
        # in the case that we're doing work with a supplier who has just been replaced ...
        # Need to remove the register interests
        # our dosend is using acks?
        self.shutdown = True
        for i in range(min(self.fileSendMaxLength, len(self.fileSendQueue))):
            fileToSend = self.fileSendDict[self.fileSendQueue[i]]
            transport_control.RemoveSupplierRequestFromSendQueue(fileToSend.packetID, fileToSend.remoteID, commands.Data())
            transport_control.RemoveInterest(fileToSend.remoteID, fileToSend.packetID)
        for i in range(min(self.fileRequestMaxLength, len(self.fileRequestQueue))):
            fileToRequest = self.fileRequestDict[self.fileRequestQueue[i]]
            transport_control.RemoveSupplierRequestFromSendQueue(fileToRequest.packetID, fileToRequest.remoteID, commands.Retrieve())
            transport_control.RemoveInterest(fileToRequest.remoteID, fileToRequest.packetID)


    def SupplierSendFile(self, fileName, packetID, ownerID, callOnAck=None, callOnFail=None):
        if self.shutdown: 
            dhnio.Dprint(8, "io_throttle.SupplierSendFile finishing to %s, shutdown is True" % self.remoteName)
            return        
        if contact_status.isOffline(self.remoteID):
            dhnio.Dprint(8, "io_throttle.SupplierSendFile %s is offline, so packet %s is failed" % (self.remoteName, packetID))
            if callOnFail is not None:
                reactor.callLater(0, callOnFail, self.remoteID, packetID, 'offline')
            return
        if packetID in self.fileSendQueue:
            # dhnio.Dprint(4, "io_throttle.SupplierSendFile WARNING packet %s already in the queue for %s" % (packetID, self.remoteName))
            if callOnFail is not None:
                reactor.callLater(0, callOnFail, self.remoteID, packetID, 'in queue')
            return
        self.fileSendQueue.append(packetID)
        self.fileSendDict[packetID] = FileToSend(
            fileName, 
            packetID, 
            self.remoteID, 
            ownerID, 
            callOnAck,
            callOnFail,)
        dhnio.Dprint(8, "io_throttle.SupplierSendFile %s to %s, queue=%d" % (packetID, self.remoteName, len(self.fileSendQueue)))
        # reactor.callLater(0, self.DoSend)
        self.DoSend()
            
            
    def RunSend(self):
        #dhnio.Dprint(6, 'io_throttle.RunSend')
        packetsFialed = []
        packetsToRemove = []
        packetsSent = 0
        # let's check all packets in the queue        
        for i in range(len(self.fileSendQueue)):
            packetID = self.fileSendQueue[i]
            fileToSend = self.fileSendDict[packetID]
            # we got notify that this packet was failed to send
            if packetID in self.sendFailedPacketIDs:
                self.sendFailedPacketIDs.remove(packetID)
                packetsFialed.append((packetID, 'failed'))
                continue
            # we already sent the file
            if fileToSend.sendTime is not None:
                packetsSent += 1
                # and we got ack
                if fileToSend.ackTime is not None:
                    deltaTime = fileToSend.ackTime - fileToSend.sendTime
                    # so remove it from queue
                    packetsToRemove.append(packetID)
                # if we do not get an ack ...    
                else:
                    # ... we do not want to wait to long
                    if time.time() - fileToSend.sendTime > fileToSend.sendTimeout:
                        # so this packet is failed because no response on it 
                        packetsFialed.append((packetID, 'timeout'))
                # we sent this packet already - check next one
                continue
            # the data file to send no longer exists - it is failed situation
            if not os.path.exists(fileToSend.fileName):
                dhnio.Dprint(4, "io_throttle.RunSend WARNING file %s not exist" % (fileToSend.fileName))
                packetsFialed.append((packetID, 'not exist'))
                continue
            # do not send too many packets, need to wait for ack
            # hold other packets in the queue and may be send next time
            if packetsSent > self.fileSendMaxLength:
                # if we sending big file - we want to wait
                # other packets must go without waiting in the queue
                # 10K seems fine, because we need to filter only Data and Parity packets here
                try:
                    if os.path.getsize(fileToSend.fileName) > 1024 * 10:
                        continue
                except:
                    dhnio.DprintException()
                    continue
            # prepare the packet
            Payload = str(dhnio.ReadBinaryFile(fileToSend.fileName))
            newpacket = dhnpacket.dhnpacket(
                commands.Data(), 
                fileToSend.ownerID, 
                self.creatorID, 
                fileToSend.packetID, 
                Payload, 
                fileToSend.remoteID)
            # outbox will not resend, because no ACK, just data, 
            # need to handle resends on own
            transport_control.outboxNoAck(newpacket)  
            transport_control.RegisterInterest(
                self.FileSendAck, 
                fileToSend.remoteID, 
                fileToSend.packetID)
            # mark file as been sent
            fileToSend.sendTime = time.time()
            packetsSent += 1
        # process failed packets
        for packetID, why in packetsFialed:
            self.FileSendFailed(self.fileSendDict[packetID].remoteID, packetID, why)
            packetsToRemove.append(packetID)
        # remove finished packets    
        for packetID in packetsToRemove:
            self.fileSendQueue.remove(packetID)
            del self.fileSendDict[packetID]
        # if sending queue is empty - remove all records about packets failed to send
        if len(self.fileSendQueue) == 0:
            del self.sendFailedPacketIDs[:]
        # remember results
        result = max(len(packetsToRemove), packetsSent)
        # erase temp lists    
        del packetsFialed
        del packetsToRemove
        return result
        

    def SendingTask(self):
        sends = self.RunSend()
        self.sendTaskDelay = misc.LoopAttenuation(
              self.sendTaskDelay, 
              sends > 0, 
              settings.MinimumSendingDelay(), 
              settings.MaximumSendingDelay())
        # attenuation
        self.sendTask = reactor.callLater(self.sendTaskDelay, self.SendingTask)
        
    
    def DoSend(self):
        #dhnio.Dprint(6, 'io_throttle.DoSend')
        if self.sendTask is None:
            self.SendingTask()
        else:
            if self.sendTaskDelay > 1.0:
                self.sendTask.cancel()
                self.sendTask = None
                self.SendingTask()
            

    def FileSendAck(self, packet):    
        if self.shutdown: 
            dhnio.Dprint(8, "io_throttle.FileSendAck finishing to %s, shutdown is True" % self.remoteName)
            return
        self.ackedCount += 1
        if packet.PacketID not in self.fileSendQueue:
            dhnio.Dprint(4, "io_throttle.FileSendAck WARNING packet %s not in sending queue for %s" % (packet.PacketID, self.remoteName))
            return
        if packet.PacketID not in self.fileSendDict.keys():
            dhnio.Dprint(4, "io_throttle.FileSendAck WARNING packet %s not in sending dict for %s" % (packet.PacketID, self.remoteName))
            return
        self.fileSendDict[packet.PacketID].ackTime = time.time()
        self.fileSendDict[packet.PacketID].result = 'acked'
        if self.fileSendDict[packet.PacketID].callOnAck:
            reactor.callLater(0, self.fileSendDict[packet.PacketID].callOnAck, packet, packet.OwnerID, packet.PacketID)
        dhnio.Dprint(8, "io_throttle.FileSendAck %s from %s, queue=%d" % (str(packet), self.remoteName, len(self.fileSendQueue)))
        self.DoSend()

        
    def FileSendFailed(self, RemoteID, PacketID, why):
        if self.shutdown: 
            dhnio.Dprint(8, "io_throttle.FileSendFailed finishing to %s, shutdown is True" % self.remoteName)
            return
        self.failedCount += 1
        if PacketID not in self.fileSendDict.keys():
            dhnio.Dprint(4, "io_throttle.FileSendFailed WARNING packet %s not in send dict" % PacketID)
            return
        self.fileSendDict[PacketID].result = why
        fileToSend = self.fileSendDict[PacketID]
        assert fileToSend.remoteID == RemoteID
        dhnio.Dprint(8, "io_throttle.FileSendFailed %s to [%s] because %s" % (PacketID, nameurl.GetName(fileToSend.remoteID), why))
        transport_control.RemoveSupplierRequestFromSendQueue(fileToSend.packetID, fileToSend.remoteID, commands.Data())
        transport_control.RemoveInterest(fileToSend.remoteID, fileToSend.packetID)
        if why == 'timeout':
            contact_status.PacketSendingTimeout(RemoteID, PacketID)
        if fileToSend.callOnFail:
            reactor.callLater(0, fileToSend.callOnFail, RemoteID, PacketID, why)
        self.DoSend()


    def SupplierRequestFile(self, callOnReceived, creatorID, packetID, ownerID):
        if self.shutdown: 
            dhnio.Dprint(8, "io_throttle.SupplierRequestFile finishing to %s, shutdown is True" % self.remoteName)
            if callOnReceived:
                reactor.callLater(0, callOnReceived, packetID, 'shutdown')
            return
        if packetID in self.fileRequestQueue:
            # dhnio.Dprint(4, "io_throttle.SupplierRequestFile WARNING packet %s already in the queue for %s" % (packetID, self.remoteName))
            if callOnReceived:
                reactor.callLater(0, callOnReceived, packetID, 'in queue')
            return
        self.fileRequestQueue.append(packetID)
        self.fileRequestDict[packetID] = FileToRequest(
            callOnReceived, creatorID, packetID, ownerID, self.remoteID)
        dhnio.Dprint(8, "io_throttle.SupplierRequestFile for %s from %s, queue length is %d" % (packetID, self.remoteName, len(self.fileRequestQueue)))
        # reactor.callLater(0, self.DoRequest)
        self.DoRequest()


    def RunRequest(self):
        #dhnio.Dprint(6, 'io_throttle.RunRequest')
        packetsToRemove = []
        for i in range(0, min(self.fileRequestMaxLength, len(self.fileRequestQueue))):
            packetID = self.fileRequestQueue[i]
            currentTime = time.time()
            if self.fileRequestDict[packetID].requestTime is not None:
                # the packet were requested
                if self.fileRequestDict[packetID].fileReceivedTime is None:
                    # but no answer yet ...
                    if currentTime - self.fileRequestDict[packetID].requestTime > self.fileRequestDict[packetID].requestTimeout:
                        # and time is out!!!
                        self.fileRequestDict[packetID].report = 'timeout' 
                        packetsToRemove.append(packetID)
                else:
                    # the packet were received (why it is not removed from the queue yet ???)
                    self.fileRequestDict[packetID].result = 'received'
                    packetsToRemove.append(packetID)
            if self.fileRequestDict[packetID].requestTime is None:
                if not os.path.exists(os.path.join(settings.getLocalBackupsDir(), packetID)): 
                    fileRequest = self.fileRequestDict[packetID]
                    dhnio.Dprint(8, "io_throttle.RunRequest for packetID " + fileRequest.packetID)
                    transport_control.RegisterInterest(
                        self.DataReceived, 
                        fileRequest.creatorID, 
                        fileRequest.packetID)
                    newpacket = dhnpacket.dhnpacket(
                        commands.Retrieve(), 
                        fileRequest.ownerID, 
                        fileRequest.creatorID, 
                        fileRequest.packetID, 
                        "", 
                        fileRequest.remoteID)
                    transport_control.outboxNoAck(newpacket)  
                    fileRequest.requestTime = time.time()
                else:
                    # we have the data file, no need to request it
                    self.fileRequestDict[packetID].result = 'exist'
                    packetsToRemove.append(packetID)
        # remember requests results
        result = len(packetsToRemove)
        # remove finished requests
        if len(packetsToRemove) > 0:
            for packetID in packetsToRemove:
                self.fileRequestQueue.remove(packetID)
        del packetsToRemove
        return result


    def RequestTask(self):
        if self.shutdown:
            return
#        if self.RunRequest() > 0:
#            self.requestTaskDelay = 0.1
#        else:
#            if self.requestTaskDelay < 8.0:
#                self.requestTaskDelay *= 2.0
        requests = self.RunRequest()
        self.requestTaskDelay = misc.LoopAttenuation(
             self.requestTaskDelay,
             requests > 0, 
             settings.MinimumReceivingDelay(), 
             settings.MaximumReceivingDelay())
        # attenuation
        self.requestTask = reactor.callLater(self.requestTaskDelay, self.RequestTask)
        
    
    def DoRequest(self):
        #dhnio.Dprint(6, 'io_throttle.DoRequest')
        if self.requestTask is None:
            self.RequestTask()
        else:
            if self.requestTaskDelay > 1.0:
                self.requestTask.cancel()
                self.requestTask = None
                self.RequestTask()


    def DataReceived(self, packet):   
        # we requested some data from a supplier, just received it
        if self.shutdown: 
            # if we're closing down this queue (supplier replaced, don't any anything new)
            return
        if packet.PacketID in self.fileRequestQueue:
            self.fileRequestQueue.remove(packet.PacketID)
        if self.fileRequestDict.has_key(packet.PacketID):
            self.fileRequestDict[packet.PacketID].fileReceivedTime = time.time()
            self.fileRequestDict[packet.PacketID].result = 'received'
            for callBack in self.fileRequestDict[packet.PacketID].callOnReceived:
                callBack(packet, 'received')
        if self.fileRequestDict.has_key(packet.PacketID):
            del self.fileRequestDict[packet.PacketID]
        dhnio.Dprint(8, "io_throttle.DataReceived %s from %s, queue=%d" % (packet, self.remoteName, len(self.fileRequestQueue)))
        self.DoRequest()


    def DeleteBackupRequests(self, backupName):
        if self.shutdown: 
            # if we're closing down this queue 
            # (supplier replaced, don't any anything new)
            return
        packetsToRemove = []
        for packetID in self.fileSendQueue:
            if packetID.find(backupName) == 0:
                self.FileSendFailed(self.fileSendDict[packetID].remoteID, packetID, 'delete request')
                packetsToRemove.append(packetID)
                dhnio.Dprint(8, 'io_throttle.DeleteBackupRequests %s from send queue' % packetID)
        for packetID in packetsToRemove:
            self.fileSendQueue.remove(packetID)
            del self.fileSendDict[packetID]
        packetsToRemove = []
        for packetID in self.fileRequestQueue:
            if packetID.find(backupName) == 0:
                packetsToRemove.append(packetID)
                dhnio.Dprint(8, 'io_throttle.DeleteBackupRequests %s from request queue' % packetID)
        for packetID in packetsToRemove:
            self.fileRequestQueue.remove(packetID)
            del self.fileRequestDict[packetID]
        if len(self.fileRequestQueue) > 0:
            reactor.callLater(0, self.DoRequest)
        if len(self.fileSendQueue) > 0:
            reactor.callLater(0, self.DoSend)
            #self.DoSend()


    def OutboxStatus(self, workitem, proto, host, status, error, message):
        packetID = workitem.packetid
        if status == 'failed' and packetID in self.fileSendQueue:
            self.sendFailedPacketIDs.append(packetID)
            # reactor.callLater(0, self.DoSend)
            self.DoSend()
            

    def HasSendingFiles(self):
        return len(self.fileSendQueue) > 0
    

    def HasRequestedFiles(self):
        return len(self.fileRequestQueue) > 0
            
  
    def OkToSend(self):
        return len(self.fileSendQueue) < self.fileSendMaxLength


    def OkToRequest(self):
        return len(self.fileRequestQueue) < self.fileRequestMaxLength
    
    
    def GetSendQueueLength(self):
        return len(self.fileSendQueue)
    
    
    def GetRequestQueueLength(self):
        return len(self.fileRequestQueue) 
            
#------------------------------------------------------------------------------ 

# all of the backup rebuilds will run their data requests through this 
# so it gets throttled, also to reduce duplicate requests
class IOThrottle:
    def __init__(self):
        self.creatorID = misc.getLocalID()
        self.supplierQueues = {} #
        self.dprintAdjust = 0
        self.paintFunc = None
        

    def SetSupplierQueueCallbackFunc(self, func):
        self.paintFunc = func


    def DeleteSuppliers(self, supplierIdentities):
        for supplierIdentity in supplierIdentities:
            if self.supplierQueues.has_key(supplierIdentity):
                self.supplierQueues[supplierIdentity].RemoveSupplierWork()
                del self.supplierQueues[supplierIdentity]


    def DeleteBackupRequests(self, backupName):
        #if settings.getDoBackupMonitor() == "Y":
        for supplierIdentity in self.supplierQueues.keys():
            self.supplierQueues[supplierIdentity].DeleteBackupRequests(backupName)


    def QueueSendFile(self, fileName, packetID, remoteID, ownerID, callOnAck=None, callOnFail=None):
        #dhnio.Dprint(8, "io_throttle.QueueSendFile %s to %s" % (packetID, nameurl.GetName(remoteID)))
        if not os.path.exists(fileName):
            dhnio.Dprint(2, "io_throttle.QueueSendFile ERROR %s not exist" % fileName)
            if callOnFail is not None:
                reactor.callLater(.01, callOnFail, remoteID, packetID, 'not exist')
            return
        if remoteID not in self.supplierQueues.keys():
            self.supplierQueues[remoteID] = SupplierQueue(remoteID, self.creatorID)
            dhnio.Dprint(6, "io_throttle.QueueSendFile made a new queue for %s" % nameurl.GetName(remoteID))
        self.supplierQueues[remoteID].SupplierSendFile(
            fileName, packetID, ownerID, callOnAck, callOnFail,)
            
            
    # return result in the callback: callOnReceived(packet or packetID, state)
    # state is: received, exist, in queue, shutdown
    def QueueRequestFile(self, callOnReceived, creatorID, packetID, ownerID, remoteID):
        # make sure that we don't actually already have the file
        #if packetID != settings.BackupInfoFileName():
        if packetID not in [ settings.BackupInfoFileName(), settings.BackupInfoFileNameOld(), settings.BackupInfoEncryptedFileName(), ]:
            filename = os.path.join(settings.getLocalBackupsDir(), packetID)
            if os.path.exists(filename):
                dhnio.Dprint(4, "io_throttle.QueueRequestFile WARNING %s already exist " % filename)
                if callOnReceived:
                    reactor.callLater(0, callOnReceived, packetID, 'exist')
                return
        if remoteID not in self.supplierQueues.keys():
            # made a new queue for this man
            self.supplierQueues[remoteID] = SupplierQueue(remoteID, self.creatorID)
            dhnio.Dprint(6, "io_throttle.QueueRequestFile made a new queue for %s" % nameurl.GetName(remoteID))
        # dhnio.Dprint(8, "io_throttle.QueueRequestFile asking for %s from %s" % (packetID, nameurl.GetName(remoteID)))
        self.supplierQueues[remoteID].SupplierRequestFile(callOnReceived, creatorID, packetID, ownerID)


    def OutboxStatus(self, workitem, proto, host, status, error, message):
#        if settings.getDoBackupMonitor() == "Y":
        for supplierIdentity in self.supplierQueues.keys():
            self.supplierQueues[supplierIdentity].OutboxStatus(workitem, proto, host, status, error, message)


    def IsSendingQueueEmpty(self):
        for idurl in self.supplierQueues.keys():
            if self.supplierQueues[idurl].HasSendingFiles():
                return False
        return True
    
    
    def IsRequestQueueEmpty(self):
        for idurl in self.supplierQueues.keys():
            if not self.supplierQueues[idurl].HasRequestedFiles():
                return False
        return True
    
    
    def HasPacketInSendQueue(self, supplierIDURL, packetID):
        if not self.supplierQueues.has_key(supplierIDURL):
            return False
        return self.supplierQueues[supplierIDURL].fileSendDict.has_key(packetID)
        
    
    def OkToSend(self, supplierIDURL):
        if not self.supplierQueues.has_key(supplierIDURL):
            # no queue opened to this man, so the queue is ready 
            return True
        return self.supplierQueues[supplierIDURL].OkToSend()
          
    
    def GetRequestQueueLength(self, supplierIDURL):
        if not self.supplierQueues.has_key(supplierIDURL):
            # no queue opened to this man, so length is zero 
            return 0
        return self.supplierQueues[supplierIDURL].GetRequestQueueLength()
        
 
    def GetSendQueueLength(self, supplierIDURL):
        if not self.supplierQueues.has_key(supplierIDURL):
            # no queue opened to this man, so length is zero 
            return 0
        return self.supplierQueues[supplierIDURL].GetSendQueueLength()


#def _debugSending(fileName, packetID, remoteID, ownerID, callOnAck=None, callOnFail=None):
##    import random
##    if random.randint(0, 3) > 1:
##        reactor.callLater(1, callOnAck, None, remoteID, packetID)
##    else:
#    dhnio.Dprint(6, 'io_throttle._debugSending ' + packetID)
#    reactor.callLater(1, callOnFail, remoteID, packetID, 'failed')
        
    
    
    
