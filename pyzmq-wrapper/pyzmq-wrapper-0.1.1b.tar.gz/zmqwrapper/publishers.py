import zmq
from sockets import ServerConnection
from constants import *

def publisher(address):
    """
    Creates a publisher binding to the given port number.

        Args:
            - address: the address to bind the PUB socket to.
    """
    return Publisher(address)
    
class Publisher(ServerConnection):
    """
    Publisher that can send messages to ZMQ
    
        Args:
            - address: the address to bind to
    """

    def __init__(self,address):
        super(Publisher,self).__init__(address,zmq.PUB)
        
        
    def publish(self,message,message_type,topic=''):
        """
        Publish the message on the PUB socket with the given topic name.
        
        Args:
            - message: the message to publish
            - message_type: the type of message being sent
            - topic: the topic on which to send the message. Defaults to ''.
        """
        super(Publisher,self).send(message,message_type,topic)

