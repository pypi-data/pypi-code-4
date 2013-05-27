'''
Test sinks
'''

from smtpd import sink, configuration
from smtpd.debug import D

def testSmtpSink():
    config = configuration.DictMapper({})
    s = sink.Smtp(config)
    D(s.mailer('google.com'))