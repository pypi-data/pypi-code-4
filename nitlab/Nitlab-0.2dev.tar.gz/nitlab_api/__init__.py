import xmlrpclib
import datetime

server_url = 'http://83.212.32.136:8085/RPC2'
server = xmlrpclib.Server(server_url);


def getNodes(filt, retValue):
    return server.scheduler.server.getNodes(filt, retValue)


def getChannels(filt, retValue):
    return server.scheduler.server.getChannels(filt, retValue)


def getTestbedInfo(filt, retValue):
    return server.scheduler.server.getTestbedInfo(filt, retValue)


def getReservedNodes(filt, retValue):
    return server.scheduler.server.getReservedNodes(filt, retValue)


def getReservedChannels(filt, retValue):
    return server.scheduler.server.getReservedChannels(filt, retValue)


def getSlices(filt, retValue):
    return server.scheduler.server.getSlices(filt, retValue)


def getUsers(filt, retValue):
    return server.scheduler.server.getUsers(filt, retValue)


def reserveNodes(filt):
    return server.scheduler.server.reserveNodes(filt)


def reserveChannels(filt):
    return server.scheduler.server.reserveChannels(filt)


def addUser(filt):
    return server.scheduler.server.addUser(filt)


def addUserToSlice(filt):
    return server.scheduler.server.addUserToSlice(filt)


def addUserKey(filt):
    return server.scheduler.server.addUserKey(filt)


def addSlice(filt):
    return server.scheduler.server.addSlice(filt)


def addNode(filt):
    return server.scheduler.server.addNode(filt)


def addChannel(filt):
    return server.scheduler.server.addChannel(filt)


def deleteKey(filt):
    return server.scheduler.server.deleteKey(filt)


def deleteNode(filt):
    return server.scheduler.server.deleteNode(filt)


def deleteUser(filt):
    return server.scheduler.server.deleteUser(filt)


def deleteUserFromSlice(filt):
    return server.scheduler.server.deleteUserFromSlice(filt)


def deleteSlice(filt):
    return server.scheduler.server.deleteSlice(filt)


def deleteChannel(filt):
    return server.scheduler.server.deleteChannel(filt)


def releaseNodes(filt):
    return server.scheduler.server.releaseNodes(filt)


def releaseChannels(filt):
    return server.scheduler.server.releaseChannels(filt)


def updateNode(filt):
    return server.scheduler.server.updateNode(filt)


def updateChannel(filt):
    return server.scheduler.server.updateChannel(filt)


def updateUser(filt):
    return server.scheduler.server.updateUser(filt)


def updateSlice(filt):
    return server.scheduler.server.updateSlice(filt)


def updateReservedNodes(filt):
    return server.scheduler.server.updateReservedNodes(filt)


def updateReservedChannels(filt):
    return server.scheduler.server.updateReservedChannels(filt)


def getServerTime():
    return datetime.datetime.now()
    return datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
