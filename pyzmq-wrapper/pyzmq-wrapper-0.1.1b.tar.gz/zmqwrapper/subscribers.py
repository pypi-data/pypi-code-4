import zmq
from sockets import ClientConnection
from constants import *
import threading

def subscriber(address,topics,callback,message_type):
    """
    Creates a subscriber binding to the given address and 
    subscribe the given topics.
    The callback is invoked for every message received.

        Args:
            - address: the address to bind the PUB socket to.
            - topics: the topics to subscribe
            - callback: the callback to invoke for every message. Must accept 2 variables - topic and message
            - message_type: the type of message to receive
    """
    return Subscriber(address,topics,callback,message_type)
    
class Subscriber(ClientConnection):
    """
    Subscriber that can read messages from ZMQ
    
        Args:
            - address: the address to bind to
            - topics: the topics to subscribe
            - callback: the callback to invoke for every message
            - message_type: the type of message to receive
    """
        
    def __init__(self,address,topics,callback,message_type):
        self._active = True
        self._topics = topics
        self._callback = callback
        self._message_type = message_type
        super(Subscriber,self).__init__(address,zmq.SUB)
        for topic in self._topics:
            self._sock.setsockopt(zmq.SUBSCRIBE,topic)
        
                    
    def _consume(self):
        while self._active:
            try:
                topic, message=super(Subscriber,self).receive(self._message_type)
                #process the message
                self._callback(topic,message)
            except zmq.ZMQError:
                pass
    
    
    def start(self):
        """
        Start a thread that consumes the messages and invokes the callback
        """
        t=threading.Thread(target=self._consume)
        t.start()
        
    def stop(self):
        """
        Stop the consumer thread
        """
        self._active = False
