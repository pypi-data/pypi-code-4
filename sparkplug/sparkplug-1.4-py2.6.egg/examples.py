import os

class EchoConsumer(object):
    def __init__(self, channel, format):
        self.channel = channel
        self.format = format
    
    def __call__(self, msg):
        print self.format % {'body': msg.body, 'pid': os.getpid()}
        self.channel.basic_ack(msg.delivery_tag)

class Broken(object):
    def __init__(self, channel):
        self.channel = channel
    
    def __call__(self, msg):
        raise ValueError(msg)
