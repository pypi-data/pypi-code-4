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


# Python imports.
from operator import attrgetter


class Rule(object):
    """
    Class representing a single iptables rule. The representation does not
    include the chain to which it is applied, or how it is applied (append vs
    insert).

    The instances of this class can be used for easily outputting a single rule.
    """
    def __init__(self, source, destination, protocol, port, description=""):
        """
        Initialises a rule instance. Sets-up the necessary information passed
        with arguments.

        Arguments:

        source - Source of communication, in format IP/NETMASK.

        destination - Destination of communication, in format IP/NETMASK.

        protocol - Protocol used by the rule. Currently supported values are
        UDP, TCP, and ICMP.

        port - Destination port in a rule if protocol specified is UDP or
        TCP. In case of ICMP this should be the ICMP packet type.

        description - Rule description. This can be used by other classes to
        produce comments in the output.
        """

        if protocol.upper() not in ("TCP", "UDP", "ICMP"):
            raise ValueError("Unsupported protocol specified: %s" % protocol)

        self.source = source
        self.destination = destination
        self.protocol = protocol.lower()
        self.port = port
        self.description = description

    def __unicode__(self):
        """
        Creates string representation of the rule. The format is:

        -s SOURCE -d DESTINATION -p PROTOCOL -m PROTOCOL (--dport|--icmp-type) PORT -j ACCEPT

        Returns:

        String representation of the rule.
        """
        if self.protocol.upper() in ("TCP", "UDP"):
            return "-s %s -d %s -p %s -m %s --dport %s -j ACCEPT" % (self.source, self.destination, self.protocol, self.protocol, self.port)
        elif self.protocol.upper() in ("ICMP"):
            return "-s %s -d %s -p %s -m %s --icmp-type %s -j ACCEPT" % (self.source, self.destination, self.protocol, self.protocol, self.port)

    def __str__(self):
        """
        Creates string representation of the rule. Calls the __unicode__
        function.

        Returns:

        String representation of the rule.
        """

        return self.__unicode__()


class LoopbackRule(object):
    """
    Static iptables rule that accepts all traffic on loopback interface.
    """

    def __init__(self):
        """
        Initialises the rule properties. Sets a static description.
        """

        self.description = "Accept all incoming traffic on loopback interface."

    def __unicode__(self):
        """
        Creates string representation of the rule. The format is:

        -i lo -j ACCEPT

        Returns:

        String representation of the rule.
        """

        return "-i lo -j ACCEPT"

    def __str__(self):
        """
        Creates string representation of the rule. Calls the __unicode__
        function.

        Returns:

        String representation of the rule.
        """

        return self.__unicode__()


class RelatedRule(object):
    """
    Static iptables rule that accepts all related traffic.
    """

    def __init__(self):
        """
        Initialises the rule properties. Sets a static description.
        """

        self.description = "Accept all incoming related traffic."

    def __unicode__(self):
        """
        Creates string representation of the rule. The format is:

        -m state --state RELATED,ESTABLISHED -j ACCEPT

        Returns:

        String representation of the rule.
        """

        return "-m state --state RELATED,ESTABLISHED -j ACCEPT"

    def __str__(self):
        """
        Creates string representation of the rule. Calls the __unicode__
        function.

        Returns:

        String representation of the rule.
        """

        return self.__unicode__()


class Chain(object):
    """
    Class representing a full iptables chain. Every chain has a name, default
    target, and contains a number of rules.

    The instances of this class can be used for easily outputting iptables rules
    for a single chain.
    """

    def __init__(self, name, default):
        """
        Initialises a chain instance. Sets-up the necessary information passed
        through the arguments.

        Arguments:

        name - The chain name (for example, INPUT, OUTPUT, FORWARD).

        default - Default target. Currently supported values are ACCEPT, DROP,
        and REJECT.
        """

        if default not in ("ACCEPT", "DROP", "REJECT"):
            raise ValueError("Unsupported default target specified: %s" % default)

        self.name = name
        self.default = default
        self.rules = []

    def add_rule(self, rule):
        """
        Adds a new rule to the chain.

        Arguments:

        rule - Instance of Rule that should be added to the chain.
        """

        self.rules.append(rule)

    def __unicode__(self):
        """
        Creates string representing of the chain. The format will be:

        :NAME DEFAULT [0:0]
        # DESC_RULE_1
        -A NAME RULE_1
        # DESC_RULE_2
        -A NAME RULE_2
        ...
        # DESC_RULE_N
        -A NAME RULE_N

        It should be noted that the rules will be grouped by their
        description. Description line is not output if description is empty.
        """

        # Set-up the "header".
        rendering = ":%s %s [0:0]" % (self.name, self.default)

        # Group the rules by description.
        rules = list(self.rules)
        rules.sort(key=attrgetter("description"))

        # Use this property to figure out if we need new line separator.
        previous_description = None

        # Process each rule.
        for rule in rules:
            if rule.description != previous_description:
                rendering += "\n"
                if rule.description:
                    rendering += "# %s\n" % rule.description
                previous_description = rule.description
            rendering += "-A %s %s\n" % (self.name, rule)
        rendering += "\n"
        return rendering

    def __str__(self):
        """
        Creates string representation of the chain. Calls the __unicode__
        function.

        Returns:

        String representation of the chain.
        """

        return self.__unicode__()


class Table(object):
    """
    Class representing a single iptables table (i.e. nat, or filter). Each table
    has a name, and a number of associated chains.

    The instances of this class can be used for easily outputting iptables rules
    for a single table.
    """

    def __init__(self, name):
        """
        Initialises a table instance. Sets-up the necessary information passed
        through the arguments.

        Arguments:

        name - Table name (for example, nat or filter).
        """
        self.name = name
        self.chains = []

    def add_chain(self, chain):
        """
        Adds a new chain to the table.

        Arguments:

        chain - Instance of Chain that should be added to the chain.
        """

        self.chains.append(chain)

    def __unicode__(self):
        """
        Creates string representing of the table. The format will be:

        *NAME
        CHAIN_1
        CHAIN_2
        COMMIT
        """

        rendering = "*%s\n" % self.name

        for chain in self.chains:
            rendering += "%s" % chain

        rendering += "COMMIT\n"

        return rendering

    def __str__(self):
        """
        Creates string representation of the table. Calls the __unicode__
        function.

        Returns:

        String representation of the table.
        """

        return self.__unicode__()
