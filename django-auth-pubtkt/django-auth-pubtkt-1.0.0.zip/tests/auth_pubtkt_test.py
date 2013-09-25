__author__ = 'Alexander Vyushkov'

import unittest
from ..auth_pubtkt import Authpubtkt

class auth_pubtkt_test(unittest.TestCase):
    def setUp(self):
        self.authpubtkt = Authpubtkt(filename = "dsa.pem")

    def test_dsa_cookie(self):
        self.authpubtkt.