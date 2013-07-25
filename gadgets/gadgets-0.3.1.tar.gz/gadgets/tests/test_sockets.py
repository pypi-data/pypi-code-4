import time, threading, random
from nose.tools import eq_
from gadgets import Addresses, Sockets, Broker

class TestSockets(object):

    def test_broker(self):
        port = random.randint(3000, 50000)
        addresses = Addresses(in_port=port, out_port=port+1, req_port=port+2)
        broker = Broker(addresses)
        sockets = Sockets(addresses)
        broker.start()
        time.sleep(0.5)
        sockets.send('shutdown', {})
        time.sleep(1)
        

    
