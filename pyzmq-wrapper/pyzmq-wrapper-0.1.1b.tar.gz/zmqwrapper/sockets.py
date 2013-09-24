import zmq
from constants import *


class SendReceiveMixin:
    """
    Provides send or receive functionality for the sockets
    """
    
    def send(self,message,message_type,topic=''):
        """
        Send the message on the socket.
        
        Args:
            - message: the message to publish
            - message_type: the type of message being sent
            - topic: the topic on which to send the message. Defaults to ''.
        """
        if message_type == RAW:
            self._sock.send(message)
        elif message_type == PYOBJ:
            self._sock.send_pyobj(message)
        elif message_type == JSON:
            self._sock.send_json(message)
        elif message_type == MULTIPART:
            self._sock.send_multipart([topic, message])
        elif message_type == STRING:
            self._sock.send_string(message)
        elif message_type == UNICODE:
            self._sock.send_unicode(message)
        else:
            raise Exception("Unknown message type %s"%(message_type,))
            
    def receive(self,message_type):
        """
        Receive the message of the specified type and retun
        
            Args:
                - message_type: the type of the message to receive
                
            Returns:
                - the topic of the message
                - the message received from the socket
        """
        topic = None
        message = None
        if message_type == RAW:
            message = self._sock.recv(flags=zmq.NOBLOCK)
        elif message_type == PYOBJ:
            message = self._sock.recv_pyobj(flags=zmq.NOBLOCK)
        elif message_type == JSON:
            message = self._sock.recv_json(flags=zmq.NOBLOCK)
        elif message_type == MULTIPART:
            data = self._sock.recv_multipart(flags=zmq.NOBLOCK)
            message = data[1]
            topic = data[0]
        elif message_type == STRING:
            message = self._sock.recv_string(flags=zmq.NOBLOCK)
        elif message_type == UNICODE:
            message = self._sock.recv_unicode(flags=zmq.NOBLOCK)
        else:
            raise Exception("Unknown message type %s"%(self._message_type,))
            
        return (topic, message)


class ServerConnection(object,SendReceiveMixin):
    """
    Creates a server side socket of given type.
    
        Args:
            - address: the address to use
            - socket_type: the tyoe of socket to open
    """

    _address = None
    _ctx = None
    _sock = None
    
    def __init__(self, address,socket_type):
        self._address = address
        self._ctx = zmq.Context()
        self._sock = self._ctx.socket(socket_type)
        self._sock.bind(address)               

    def sock(self):
        """
        Returns the zmq socket object being used for the connection. This can be used
        to send messages with additional flags etc.
        
            Returns:
                - The underlying zmq socket
        """
        return self._sock
        
    def close(self):
        """
        Close the socket connection.
        """
        self._sock.close()

class ClientConnection(object,SendReceiveMixin):
    """
    Creates a client side socket of given type.
    
        Args:
            - address: the address to use
            - socket_type: the tyoe of socket to open
    """

    _address = None
    _ctx = None
    _sock = None
    
    def __init__(self, address,socket_type):
        self._address = address
        self._ctx = zmq.Context()
        self._sock = self._ctx.socket(socket_type)
        self._sock.connect(address)               

    def sock(self):
        """
        Returns the zmq socket object being used for the connection. This can be used
        to receive messages with additional flags etc.
        
            Returns:
                - The underlying zmq socket
        """
        return self._sock

    def close(self):
        """
        Close the socket connection.
        """
        self._sock.close()        
