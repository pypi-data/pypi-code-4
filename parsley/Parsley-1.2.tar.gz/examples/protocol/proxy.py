from twisted.internet.defer import Deferred
from twisted.internet.endpoints import TCP4ServerEndpoint, clientFromString
from twisted.internet.error import ConnectionLost, ConnectionAborted
from twisted.internet.task import react
from twisted.python.failure import Failure
from twisted.tubes.itube import ISwitchablePump
from twisted.tubes.protocol import factoryFromFlow
from twisted.tubes.tube import Pump, cascade
from zope.interface import implementer

from parsley import makeProtocol


@implementer(ISwitchablePump)
class _ParsleyPump(Pump):
    def __init__(self, protocol):
        self.protocol = protocol
        self.protocol.pump = self

    def started(self):
        self.protocol.makeConnection(self.tube)

    def received(self, string):
        print 'got', `string`
        self.protocol.dataReceived(string)
        print 'done getting'

    def stopped(self, reason):
        self.protocol.connectionLost(reason)

    def reassemble(self, data):
        print 'reassemble', data
        return [arg for command, arg in data]


def flowWithParsley(fount, protocol, drain):
    return fount.flowTo(cascade(_ParsleyPump(protocol))).flowTo(drain)


grammar = """

delimiter = '\r'? '\n'
line = <(~delimiter anything)+>:line delimiter -> line
endpoint = 'endpoint:' <(~'!' anything)+>:endpoint '!' -> receiver.gotEndpoint(endpoint)
echo = line:line -> receiver.gotEcho(line)
incoming = endpoint | echo

"""


class ProxySender(object):
    def __init__(self, tube):
        self.tube = tube

    def sendCommand(self, command, arg):
        print 'delivering', command, arg
        self.tube.deliver((command, arg))


class ProxyReceiver(object):
    currentRule = 'incoming'

    def __init__(self, sender):
        self.sender = sender

    def prepareParsing(self, parser):
        pass

    def finishParsing(self, reason):
        reason.printTraceback()

    def gotEcho(self, line):
        self.sender.sendCommand('echo', line)

    def gotEndpoint(self, description):
        self.sender.sendCommand('endpoint', description)


@implementer(ISwitchablePump)
class _NullPump(Pump):
    def __init__(self):
        self._buffer = []

    def received(self, item):
        self._buffer.append(item)

    def reassemble(self, data):
        assert data == []
        return self._buffer


def switchEventually(tube, deferred):
    pump = _NullPump()
    tube.switch(cascade(pump))
    def cb(drain):
        pump.tube.switch(drain)
    deferred.addCallback(cb)


class ProxyPump(Pump):
    def __init__(self, fount, drain, switchPump, reactor):
        self.incomingFount = fount
        self.incomingDrain = drain
        self.switchPump = switchPump
        self.reactor = reactor

    def received(self, data):
        print data
        command, arg = data
        if command == 'echo':
            self.tube.deliver(arg + '\r\n')
        elif command == 'endpoint':
            d = Deferred()
            switchEventually(self.switchPump.tube, d)
            endpoint = clientFromString(self.reactor, arg)
            def outgoing(connectingFount, connectingDrain):
                print 'connected'
                d.callback(connectingDrain)
                connectingFount.flowTo(self.incomingDrain)
            self.reactor.callLater(2, endpoint.connect, factoryFromFlow(outgoing))



def echoFlow(reactor):
    def flow(fount, drain):
        parsleyPump = _ParsleyPump(makeProtocol(grammar, ProxySender, ProxyReceiver)())
        return fount.flowTo(cascade(
            parsleyPump,
            ProxyPump(fount, drain, parsleyPump, reactor),
        ))#.flowTo(drain)
    return flow

def main(reactor):
    server = TCP4ServerEndpoint(reactor, 1234)
    d = server.listen(factoryFromFlow(echoFlow(reactor)))
    d.addCallback(lambda ign: Deferred())
    return d

react(main, [])
