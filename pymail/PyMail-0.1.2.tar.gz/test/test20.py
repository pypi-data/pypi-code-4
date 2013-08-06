
from pymail.pymail import server
import os
from unittest import TestCase

class ServerHelpTest(TestCase):
    def testServerHelp(self, ):
        with self.assertRaises(SystemExit):
            s = server.Server(['-h'])

def testCreateServer():
    s = server.Server(['-c', os.path.join(os.getcwd(), 'test', 'config0')])

def testStartServer():
    s = server.Server(['-c', os.path.join(os.getcwd(), 'test', 'config1')])
    s.start(False)
