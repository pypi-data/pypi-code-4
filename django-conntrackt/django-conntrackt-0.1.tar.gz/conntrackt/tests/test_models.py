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
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

# Application imports.
from conntrackt.models import Project, Location, Entity, Interface, Communication

# Test imports.
from .factories import ProjectFactory, LocationFactory
from .factories import ServerEntityFactory, ServerInterfaceFactory
from .factories import SubnetEntityFactory, SubnetInterfaceFactory
from .factories import CommunicationFactory
from .factories import setup_test_data


class ProjectTest(TestCase):

    def test_unique_name(self):
        """
        Test if unique project name is enforced.
        """

        project = ProjectFactory()

        self.assertRaises(IntegrityError, ProjectFactory, name=project.name)

    def test_representation(self):
        """
        Test the representation of project.
        """

        project = ProjectFactory(name="Test Project")

        self.assertEqual(str(project), "Test Project")

    def test_absolute_url(self):
        """
        Tests if the absolute URL is generated properly.
        """

        project = ProjectFactory(pk=1)

        self.assertEqual(project.get_absolute_url(), "/conntrackt/project/1/")


class LocationTest(TestCase):

    def test_unique_name(self):
        """
        Test if unique location name is enforced.
        """

        location = LocationFactory()

        self.assertRaises(IntegrityError, LocationFactory, name=location.name)

    def test_representation(self):
        """
        Test the representation of location.
        """

        project = LocationFactory(name="Test Location")

        self.assertEqual(str(project), "Test Location")


class EntityTest(TestCase):

    def setUp(cls):
        """
        Set-up some test data.
        """

        setup_test_data()

    def test_incoming_communications(self):
        """
        Test that we get correct list of incoming connections with the sample
        data.
        """

        entity = Entity.objects.get(pk=1)
        incoming = Communication.objects.filter(pk__in=(1, 2, 3, 5))

        self.assertItemsEqual(entity.incoming_communications(), incoming)

    def test_outgoing_communications(self):
        """
        Test that we get correct list of outgoing connections with the sample
        data.
        """

        entity = Entity.objects.get(pk=1)
        outgoing = Communication.objects.filter(pk__in=(4, 6))

        self.assertItemsEqual(entity.outgoing_communications(), outgoing)

    def test_representation(self):
        """
        Test the representation of entity.
        """

        ent = Entity.objects.get(pk=1)
        representation = "Test Entity 1 (Test Project 1 - Test Location 1)"

        self.assertEqual(str(ent), representation)

    def test_unique_name(self):
        """
        Test if unique entity name is enforced across same project.
        """

        entity1 = Entity.objects.get(pk=1)

        entity_dup = Entity(name=entity1.name, description="Duplicate entity.", project=entity1.project, location=entity1.location)

        self.assertRaises(IntegrityError, entity_dup.save)

    def test_absolute_url(self):
        """
        Tests if the absolute URL is generated properly.
        """

        entity = Entity.objects.get(pk=1)

        self.assertEqual(entity.get_absolute_url(), "/conntrackt/entity/1/")

    def test_project_move_constraints(self):
        """
        Tests if entity is prevented from being moved to different project in
        case of existing communications.
        """

        entity = Entity.objects.get(pk=1)
        new_project = Project.objects.get(pk=2)

        entity.project = new_project
        self.assertRaisesRegexp(ValidationError, "The entity cannot be moved to different project as long as it has valid communications with entities in current project.", entity.clean)


class InterfaceTest(TestCase):

    def setUp(self):
        """
        Set-up some test data.
        """

        setup_test_data()

    def test_unique_name(self):
        """
        Test if unique interface name is enforced across same entity.
        """

        entity = Entity.objects.get(pk=1)

        interface = entity.interface_set.get(pk=1)

        duplicate = Interface(name=interface.name, description="Duplicate interface.", entity=entity, address="10.10.10.10", netmask="255.255.255.255")

        self.assertRaises(IntegrityError, duplicate.save)

    def test_unique_address(self):
        """
        Test if unique address/netmask is enforced across same entity.
        """

        entity = Entity.objects.get(pk=1)

        interface = entity.interface_set.get(pk=1)

        duplicate = Interface(name="eth1", description="Duplicate address", entity=entity, address=interface.address, netmask=interface.netmask)

        self.assertRaises(IntegrityError, duplicate.save)

    def test_representation_single(self):
        """
        Test representation of single IP address.
        """

        interface = Entity.objects.get(name="Test Entity 1").interface_set.get(name="eth0")
        representation = "Test Entity 1 (192.168.1.1)"

        self.assertEqual(str(interface), representation)

    def test_representation_subnet(self):
        """
        Test representation of subnet.
        """

        interface = Entity.objects.get(pk=4).interface_set.get(name="switch0")
        representation = "Test Subnet 4 (10.10.4.0/255.255.255.0)"

        self.assertEqual(str(interface), representation)


class CommunicationTest(TestCase):

    def setUp(self):
        """
        Set-up some test data.
        """

        setup_test_data()

    def test_unique_communication(self):
        """
        Test enforcement of unique communications.
        """

        comm = Communication.objects.get(pk=1)

        self.assertRaises(IntegrityError, Communication.objects.create, source=comm.source, destination=comm.destination, protocol=comm.protocol, port=comm.port, description="Duplicate communication.")

    def test_project_same(self):
        """
        Test enforcement of same project entities for communications.
        """

        ent1 = Entity.objects.get(pk=1)
        ent1_eth0 = ent1.interface_set.get(name="eth0")
        ent5 = Entity.objects.get(pk=5)
        ent5_eth0 = ent5.interface_set.get(name="eth0")

        # Set-up a communication between different projects.
        comm = Communication.objects.create(source=ent1_eth0, destination=ent5_eth0, protocol="ICMP", port="8", description="Ping.")

        self.assertRaisesRegexp(ValidationError, 'Source and destination entities do not belong to the same project', comm.full_clean)

    def test_same_entity(self):
        """
        Test enforcement of differing entities for communication.
        """

        ent = Entity.objects.get(pk=1)
        ent_eth0 = ent.interface_set.get(name="eth0")

        # Set-up a communication between same entity.
        comm = Communication.objects.create(source=ent_eth0, destination=ent_eth0, protocol="ICMP", port="8", description="Ping.")

        self.assertRaisesRegexp(ValidationError, "Source and destination entities are identical.", comm.full_clean)

    def test_unsupported_protocol(self):
        """
        Test enforcement of supported protocol.
        """

        ent1 = Entity.objects.get(pk=1)
        ent1_eth0 = ent1.interface_set.get(name="eth0")
        ent2 = Entity.objects.get(pk=2)
        ent2_eth0 = ent2.interface_set.get(name="eth0")

        comm = Communication(source=ent1_eth0, destination=ent2_eth0, protocol="BOGUS", port="1234")

        self.assertRaisesRegexp(ValidationError, "BOGUS is not a supported protocol.", comm.full_clean)

    def test_edit_link(self):
        """
        Tests the function for getting the edit link string.
        """

        comm = Communication.objects.get(pk=1)

        self.assertEqual("Edit", comm.edit_link())

    def test_representation(self):
        """
        Test the representation of communication.
        """

        comm = Communication.objects.get(pk=1)

        expected = "Test Entity 2 -> Test Entity 1 (TCP:22)"

        self.assertEqual(expected, str(comm))

    def test_source_representation(self):
        """
        Test the representation of communication from source perspective.
        """

        comm = Communication.objects.get(pk=1)

        expected = "Test Entity 2 (192.168.1.2) - TCP: 22"

        self.assertEqual(expected, comm.source_representation())

    def test_destination_representation(self):
        """
        Test the representation of communication from destination perspective.
        """

        comm = Communication.objects.get(pk=1)

        expected = "Test Entity 1 (192.168.1.1) - TCP: 22"

        self.assertEqual(expected, comm.destination_representation())
