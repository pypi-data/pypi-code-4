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


# Third-party application imports.
import factory

# Application imports.
from conntrackt.models import Project, Location, Entity, Interface, Communication


class ProjectFactory(factory.django.DjangoModelFactory):
    """
    Factory for producing projects where name is set to "Test Project N", and N
    is an increasing sequence. Description is based on name.
    """

    FACTORY_FOR = Project

    @factory.sequence
    def name(n):
        return "Test Project %d" % n

    description = factory.LazyAttribute(lambda d: "This is %s." % d.name)


class LocationFactory(factory.django.DjangoModelFactory):
    """
    Factory for producing locations where name is set to "Test Location N", and
    N is an increasing sequence. Description is based on name.
    """

    FACTORY_FOR = Location

    @factory.sequence
    def name(n):
        return "Test Location %d" % n

    description = factory.LazyAttribute(lambda d: "This is %s." % d.name)


class ServerInterfaceFactory(factory.django.DjangoModelFactory):
    """
    Factory for producing server interfaces. Interface IP address is set to
    192.168.1.N, where N is a sequence. The netmask is always set to
    "255.255.255.255". The interface name is always set to eth0.
    """

    FACTORY_FOR = Interface
    netmask = "255.255.255.255"
    name = "eth0"

    @factory.sequence
    def address(n):
        return "192.168.1.%d" % (n)


class SubnetInterfaceFactory(factory.django.DjangoModelFactory):
    """
    Factory for producing subnet "interfaces". Interface IP address is set to
    10.10.N.0, where N is a sequence. Interface name is always set to
    switch0. Netmask is set to "255.255.255.0".
    """

    FACTORY_FOR = Interface
    netmask = "255.255.255.0"
    name = "switch0"

    @factory.sequence
    def address(n):
        return "10.10.%d.0" % (n)


class ServerEntityFactory(factory.django.DjangoModelFactory):
    """
    Factory for producing server entities where name is set to "Test Entity N",
    and N is an increasing sequence.
    """

    FACTORY_FOR = Entity

    interface = factory.RelatedFactory(ServerInterfaceFactory, "entity")

    @factory.sequence
    def name(n):
        return "Test Entity %d" % n

    description = factory.LazyAttribute(lambda d: "This is %s." % d.name)


class SubnetEntityFactory(factory.django.DjangoModelFactory):
    """
    Factory for producing subnet entities where name is set to "Test Subnet N",
    and N is an increasing sequence.
    """

    FACTORY_FOR = Entity

    interface = factory.RelatedFactory(SubnetInterfaceFactory, "entity")

    @factory.sequence
    def name(n):
        return "Test Subnet %d" % n

    description = factory.LazyAttribute(lambda d: "This is %s." % d.name)


class CommunicationFactory(factory.django.DjangoModelFactory):
    """
    Factory for producing communications. The descriptin of communication will
    be based on protocol and port.
    """

    FACTORY_FOR = Communication

    description = factory.LazyAttribute(lambda d: "Communicate over %s:%s" % (d.protocol, d.port))


def setup_test_data():
    """
    Sets-up some test data for testing more complex functionality.
    """

    for factory in ProjectFactory, LocationFactory, ServerEntityFactory, SubnetEntityFactory, ServerInterfaceFactory, SubnetInterfaceFactory, CommunicationFactory:
        factory.reset_sequence()

    project1 = ProjectFactory(pk=1)
    project2 = ProjectFactory(pk=2)

    location1 = LocationFactory(pk=1)
    location2 = LocationFactory(pk=2)

    entity1 = ServerEntityFactory(pk=1, project=project1, location=location1)
    entity2 = ServerEntityFactory(pk=2, project=project1, location=location1)
    entity3 = ServerEntityFactory(pk=3, project=project1, location=location2)
    entity4 = SubnetEntityFactory(pk=4, project=project1, location=location2)
    entity5 = ServerEntityFactory(pk=5, project=project2, location=location1)

    communication1 = CommunicationFactory(pk=1, source_id=2, destination_id=1, protocol="TCP", port="22")
    communication2 = CommunicationFactory(pk=2, source_id=2, destination_id=1, protocol="ICMP", port="8")
    communication3 = CommunicationFactory(pk=3, source_id=3, destination_id=1, protocol="TCP", port="3306")
    communication4 = CommunicationFactory(pk=4, source_id=1, destination_id=3, protocol="UDP", port="53")
    communication5 = CommunicationFactory(pk=5, source_id=4, destination_id=1, protocol="TCP", port="22")
    communication6 = CommunicationFactory(pk=6, source_id=1, destination_id=2, protocol="UDP", port="123")
