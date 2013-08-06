
import os
from pymail.pymail.configuration import Configuration

def testConfiguration():
    c = Configuration(os.path.join(os.getcwd(), 'test', 'config1'))

def testConfigurationExistingValue():
    c = Configuration(os.path.join(os.getcwd(), 'test', 'config3'))
    assert c.servers.smtp.interface == '0.0.0.0'

def testConfigurationGetExistingValue():
    c = Configuration(os.path.join(os.getcwd(), 'test', 'config1'))
    assert c('key') == 'value'

def testConfigurationGetExistingValue():
    c = Configuration(os.path.join(os.getcwd(), 'test', 'config1'))
    assert c('nonexistent-key') is None