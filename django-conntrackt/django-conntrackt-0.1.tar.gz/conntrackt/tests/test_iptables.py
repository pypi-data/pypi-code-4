# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Branko Majic
#
# This file is part of Django Conntrackt.
#
# Django Conntrackt is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Django Conntrackt is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# Django Conntrackt.  If not, see <http://www.gnu.org/licenses/>.
#


# Django imports.
from django.test import TestCase

# Application imports.
from conntrackt import iptables


class RuleTest(TestCase):
    def test_output_case(self):
        """
        Test that protocol name is lower-cased during rule generation.
        """

        rule = iptables.Rule("192.168.1.1/255.255.255.255", "192.168.1.2/255.255.255.255", "tCp", "80", description="Web server.")
        self.assertEqual(str(rule), "-s 192.168.1.1/255.255.255.255 -d 192.168.1.2/255.255.255.255 -p tcp -m tcp --dport 80 -j ACCEPT")

    def test_output_tcp(self):
        """
        Tests that a TCP rule is generated properly.
        """

        rule = iptables.Rule("192.168.1.1/255.255.255.255", "192.168.1.2/255.255.255.255", "TCP", "80", description="Web server.")
        self.assertEqual(str(rule), "-s 192.168.1.1/255.255.255.255 -d 192.168.1.2/255.255.255.255 -p tcp -m tcp --dport 80 -j ACCEPT")

    def test_output_udp(self):
        """
        Tests that a UDP rule is generated properly.
        """

        rule = iptables.Rule("192.168.1.1/255.255.255.255", "192.168.1.2/255.255.255.255", "UDP", "53", description="DNS server.")
        self.assertEqual(str(rule), "-s 192.168.1.1/255.255.255.255 -d 192.168.1.2/255.255.255.255 -p udp -m udp --dport 53 -j ACCEPT")

    def test_output_icmp(self):
        """
        Tests that an ICMP rule is generated properly.
        """

        rule = iptables.Rule("192.168.1.1/255.255.255.255", "192.168.1.2/255.255.255.255", "ICMP", "8", description="Ping.")
        self.assertEqual(str(rule), "-s 192.168.1.1/255.255.255.255 -d 192.168.1.2/255.255.255.255 -p icmp -m icmp --icmp-type 8 -j ACCEPT")

    def test_unsupported_protocol(self):
        """
        Tests that unsupported protocol will raise an exception.
        """

        self.assertRaises(ValueError, iptables.Rule, "192.168.1.1/255.255.255.255", "192.168.1.2/255.255.255.255",
                          "NONEXIST", "8", description="Non-existing")


class LoopbackRuleTest(TestCase):
    def test_output(self):
        """
        Tests that a loopback rule is generated properly.
        """

        rule = iptables.LoopbackRule()
        self.assertEqual(str(rule), "-i lo -j ACCEPT")


class RelatedRuleTest(TestCase):
    def test_output(self):
        """
        Tests that a related rule is generated properly.
        """

        rule = iptables.RelatedRule()
        self.assertEqual(str(rule), "-m state --state RELATED,ESTABLISHED -j ACCEPT")


class ChainTest(TestCase):
    def test_output_empty(self):
        """
        Test generation of empty chain.
        """

        chain = iptables.Chain("INPUT", "ACCEPT")
        self.assertEqual(str(chain), ":INPUT ACCEPT [0:0]\n")

    def test_unsupported_protocol(self):
        """
        Tests that unsupported target will raise an exception.
        """

        self.assertRaises(ValueError, iptables.Chain, "INPUT", "NOTARGET")

    def test_add_rule(self):
        """
        Tests that the rule is being added to the chain properly.
        """

        chain = iptables.Chain("INPUT", "ACCEPT")
        rule = iptables.Rule("192.168.1.1/255.255.255.255", "192.168.1.2/255.255.255.255", "TCP", "22", "SSH")
        chain.add_rule(rule)

        self.assertItemsEqual(chain.rules, [rule])

    def test_output(self):
        """
        Tests that a chain is generated properly.
        """

        chain = iptables.Chain("INPUT", "ACCEPT")

        chain.add_rule(iptables.Rule("192.168.1.1/255.255.255.255", "192.168.1.2/255.255.255.255", "TCP", "80", "Web server"))
        chain.add_rule(iptables.Rule("192.168.1.1/255.255.255.255", "192.168.1.3/255.255.255.255", "TCP", "80", "Web server"))

        chain.add_rule(iptables.Rule("192.168.1.1/255.255.255.255", "192.168.1.2/255.255.255.255", "TCP", "22", "SSH"))
        chain.add_rule(iptables.Rule("192.168.1.1/255.255.255.255", "192.168.1.3/255.255.255.255", "TCP", "22", ""))

        expected_output = """:INPUT ACCEPT [0:0]
-A INPUT -s 192.168.1.1/255.255.255.255 -d 192.168.1.3/255.255.255.255 -p tcp -m tcp --dport 22 -j ACCEPT

# SSH
-A INPUT -s 192.168.1.1/255.255.255.255 -d 192.168.1.2/255.255.255.255 -p tcp -m tcp --dport 22 -j ACCEPT

# Web server
-A INPUT -s 192.168.1.1/255.255.255.255 -d 192.168.1.2/255.255.255.255 -p tcp -m tcp --dport 80 -j ACCEPT
-A INPUT -s 192.168.1.1/255.255.255.255 -d 192.168.1.3/255.255.255.255 -p tcp -m tcp --dport 80 -j ACCEPT

"""

        self.assertEqual(str(chain), expected_output)


class TableTest(TestCase):
    def test_output_empty(self):
        """
        Tests that an empty table is generated properly.
        """

        table = iptables.Table("filter")
        self.assertEqual(str(table), "*filter\nCOMMIT\n")

    def test_output(self):
        """
        Tests that a table is generated properly.
        """

        table = iptables.Table("filter")
        table.add_chain(iptables.Chain("INPUT", "ACCEPT"))
        table.add_chain(iptables.Chain("OUTPUT", "ACCEPT"))
        table.add_chain(iptables.Chain("FORWARD", "ACCEPT"))

        expected_output = """*filter
:INPUT ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]
:FORWARD ACCEPT [0:0]
COMMIT
"""
        self.assertEqual(str(table), expected_output)

    def test_add_chain(self):
        """
        Tests that the chain is being added to the table properly.
        """

        table = iptables.Table("filter")
        chain = iptables.Chain("INPUT", "ACCEPT")
        table.add_chain(chain)

        self.assertItemsEqual(table.chains, [chain])
