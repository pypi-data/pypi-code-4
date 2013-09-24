import zmq
from sockets import ClientConnection
from constants import *
import threading

def requestor(address,callback,message_type):
    """
    Creates a requestor binding to the given address send requests.
    The callback is invoked for every reply received.

        Args:
            - address: the address to bind the REQ socket to.
            - callback: the callback to invoke for every message. Must accept 2 variables - message and the requestor
            - message_type: the type of message to receive
    """
    return Requestor(address,callback,message_type)
    
class Requestor(ClientConnection):
    """
    Requestor that that can send requests of given type
    
        Args:
            - address: the address to bind to
            - callback: the callback to invoke for every reply
            - message_type: the type of request to send
    """
        
    def __init__(self,address,callback,message_type):
        self._active = True
        self._callback = callback
        self._message_type = message_type
        super(Requestor,self).__init__(address,zmq.REQ)
        
                    
    def _consume(self):
        while self._active:
            try:
                topic, message=super(Requestor,self).receive(self._message_type)
                #process the message
                self._callback(message,self)
            except zmq.ZMQError:
                pass
    
    
    def start(self):
        """
        Start a thread that consumes the replies and invokes the callback
        """
        t=threading.Thread(target=self._consume)
        t.start()
        
    def stop(self):
        """
        Stop the consumer thread
        """
        self._active = False
        
    def request(self,message,message_type):
        """
        Send a request message of the given type
        
        Args:
            - message: the message to publish
            - message_type: the type of message being sent
        """
        if message_type == MULTIPART:
            raise Exception("Unsupported request type")
            
        super(Requestor,self).send(message,message_type)
    
