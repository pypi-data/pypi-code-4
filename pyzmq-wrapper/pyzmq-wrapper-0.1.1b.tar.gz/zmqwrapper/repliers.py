import zmq
from sockets import ServerConnection
from constants import *
import threading

def replier(address,callback,message_type):
    """
    Creates a replier binding to the given address send replies.
    The callback is invoked for every request received.

        Args:
            - address: the address to bind the REP socket to.
            - callback: the callback to invoke for every message. Must accept 2 variables - message and the replier
            - message_type: the type of message to receive
    """
    return Replier(address,callback,message_type)
    
class Replier(ServerConnection):
    """
    Requestor that that can respond to requests of given type
    
        Args:
            - address: the address to bind to
            - callback: the callback to invoke for every request
            - message_type: the type of reply to send
    """
        
    def __init__(self,address,callback,message_type):
        self._active = True
        self._callback = callback
        self._message_type = message_type
        super(Replier,self).__init__(address,zmq.REP)
        
                    
    def _consume(self):
        while self._active:
            try:
                topic, message=super(Replier,self).receive(self._message_type)
                #process the message
                self._callback(message,self)
            except zmq.ZMQError:
                pass
    
    
    def start(self):
        """
        Start a thread that consumes the requests and invokes the callback
        """
        t=threading.Thread(target=self._consume)
        t.start()
        
    def stop(self):
        """
        Stop the consumer thread
        """
        self._active = False
        
    def reply(self,message,message_type):
        """
        Send a reply message of the given type
        
        Args:
            - message: the message to publish
            - message_type: the type of message being sent
        """
        if message_type == MULTIPART:
            raise Exception("Unsupported reply type")
            
        super(Replier,self).send(message,message_type)
    
