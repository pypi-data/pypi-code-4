'''
Test sinks
'''

from pymail.pymail import sink, configuration
from pymail.pymail.debug import D

def testSmtpSink():
    config = configuration.DictMapper({})
    s = sink.Smtp(config)
    D(s.mailer('google.com'))