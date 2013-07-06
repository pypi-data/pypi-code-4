import json

from txjsonrpc.jsonrpc import BaseSubhandler
from txjsonrpc import jsonrpclib
from twisted.protocols import basic

from txjsonrpc.netstring import jsonrpc


class LineJsonRpc(basic.LineReceiver, jsonrpc.JSONRPC):

    delimiter = '\n'

    def lineReceived(self, line):
        self.stringReceived(line)

    def sendString(self, line):
        self.sendLine(line)


class JsonProtocol(jsonrpc.JSONRPC, object):
    """
    Compatibility layer to make jsonrpc.JSONRPC actually behave!
    """

    def __init__(self):
        """
        Call ALL superclass __init__ methods.
        """
        jsonrpc.JSONRPC.__init__(self)
        BaseSubhandler.__init__(self)

    def _cbRender(self, result, req_id):
        """
        A result is a result, I don't want to wrap it in a list.
        """
        if req_id is None:
            # This was a notification, don't bother
            return
        try:
            s = jsonrpclib.dumps(result, id=req_id, version=self.version)
        except:
            f = jsonrpclib.Fault(self.FAILURE, "can't serialize output")
            s = jsonrpclib.dumps(f, id=req_id, version=self.version)
        return self.sendString(s)

    def connectionMade(self):
        self.MAX_LENGTH = self.factory.maxLength
        for handler in self.subHandlers.itervalues():
            handler.transport = self.transport

    def connectionLost(self, reason):
        for handler in self.subHandlers.itervalues():
            handler.connectionLost(reason)

    def notify(self, func, *args):
        payload = {
            'method': func,
            'params': args,
        }
        self.sendString(json.dumps(payload))
