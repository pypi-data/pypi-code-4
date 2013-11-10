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

# Standard Python library import.
import collections

# Python third-party library imports.
import mock
from palette import Color

# Django imports.
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Model
from django.test import TestCase

# Application imports.
from conntrackt.models import Project, Location, Entity, Interface, Communication
from conntrackt.models import SearchManager
from conntrackt.models import NestedObjects
from conntrackt.utils import list_formatter_callback

# Test imports.
from .factories import ProjectFactory, LocationFactory
from .factories import ServerEntityFactory, ServerInterfaceFactory
from .factories import SubnetEntityFactory, SubnetInterfaceFactory
from .factories import CommunicationFactory
from .factories import setup_test_data


class RelatedCollectorMixinTest(TestCase):

    @mock.patch.object(NestedObjects, "collect")
    @mock.patch.object(NestedObjects, "nested")
    def test_get_dependant_objects_method_calls(self, nested_mock, collect_mock):
        """
        Tests if correct methods are being called with correct arguments during
        the invocation of get_dependant_objects method.
        """

        # Set-up some test data.
        project = ProjectFactory()

        # Call the method.
        project.get_dependant_objects()

        # Check if correct collector methods were called.
        collect_mock.assert_called_with([project])
        nested_mock.assert_called_with()

    def test_get_dependant_objects_return_value(self):
        """
        Tests the return value of get_dependant_objects method.
        """

        # Set-up some test data.
        project = ProjectFactory()
        location = LocationFactory()
        entity1 = ServerEntityFactory(pk=1, project=project, location=location)
        entity2 = ServerEntityFactory(pk=2, project=project, location=location)
        communication1 = CommunicationFactory(pk=1, source_id=1, destination_id=2, protocol="TCP", port="22")

        # Get the dependant objects.
        dependant_objects = project.get_dependant_objects()

        # Create a small local function for traversing the recursive list.
        def traverse(data):
            # If data is iterable, verify it is a list, and process its members
            # as well. If data is not iterable, make sure it is descendant of
            # Django Model class.
            if isinstance(data, collections.Iterable):
                self.assertIsInstance(data, list)
                for element in data:
                    traverse(element)
            else:
                self.assertIsInstance(data, Model)

        # Traverse the obtained dependant objects.
        traverse(dependant_objects)

    @mock.patch.object(NestedObjects, "collect")
    @mock.patch.object(NestedObjects, "nested")
    def test_get_dependant_objects_representation_method_calls(self, nested_mock, collect_mock):
        """
        Tests if correct methods are being called with correct arguments during
        the invocation of get_dependant_objects method.
        """

        # Set-up some test data.
        project = ProjectFactory()

        # Call the method.
        project.get_dependant_objects_representation()

        # Check if correct collector methods were called.
        collect_mock.assert_called_with([project])
        nested_mock.assert_called_with(list_formatter_callback)

    def test_get_dependant_objects_representation_return_value(self):
        """
        Tests the return value of get_dependant_objects_representation method.
        """

        # Set-up some test data.
        project = ProjectFactory()
        location = LocationFactory()
        entity1 = ServerEntityFactory(pk=1, project=project, location=location)
        entity2 = ServerEntityFactory(pk=2, project=project, location=location)
        communication1 = CommunicationFactory(pk=1, source_id=1, destination_id=2, protocol="TCP", port="22")

        # Get the dependant objects.
        dependant_objects = project.get_dependant_objects_representation()

        # Create a small local function for traversing the recursive list.
        def traverse(data):
            # If data is iterable, verify it is a list, and process its members
            # as well. If data is not iterable, make sure it is descendant of
            # Django Model class.
            if isinstance(data, collections.Iterable) and not isinstance(data, str):
                self.assertIsInstance(data, list)
                for element in data:
                    traverse(element)
            else:
                self.assertIsInstance(data, str)

        # Traverse the obtained dependant objects.
        traverse(dependant_objects)


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

    def test_custom_manager(self):
        """
        Tests if the custom manager is being used.
        """

        self.assertIsInstance(Project.objects, SearchManager)

    def test_get_project_communications_summary_count(self):
        """
        Test if the method returns correct number of entries in the list.
        """

        # Set-up some test data to work with.
        setup_test_data()

        # Get the first project from test data.
        project = Project.objects.get(pk=1)

        # Fetch the project communications
        communications = project.get_project_communications_summary()

        # Validate the number of returned communications.
        self.assertEqual(len(communications), 6)

    def test_get_project_communications_summary_return_value(self):
        """
        Test if the method returns correct type.
        """

        # Set-up some test data.
        setup_test_data()

        # Fetch one of the projects.
        project = Project.objects.get(pk=1)

        # Get the communications summary for the project.
        communications = project.get_project_communications_summary()

        # Validate the return value type.
        self.assertIsInstance(communications, list)

        # Perform verification on every summary element returned.
        for comm in communications:
            # Verify the type of element and its size.
            self.assertIsInstance(comm, dict)
            self.assertEqual(len(comm), 6)

            # Verify the presence of correct dictionary keys.
            keys = comm.keys()
            self.assertIn("source", keys)
            self.assertIn("source_color", keys)
            self.assertIn("destination", keys)
            self.assertIn("destination_color", keys)
            self.assertIn("protocol", keys)
            self.assertIn("port", keys)

            # Verify the value types.
            self.assertIsInstance(comm["source"], unicode)
            self.assertIsInstance(comm["source_color"], Color)
            self.assertIsInstance(comm["destination"], unicode)
            self.assertIsInstance(comm["destination_color"], Color)
            self.assertIsInstance(comm["protocol"], unicode)
            self.assertIsInstance(comm["port"], int)


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

    def test_custom_manager(self):
        """
        Tests if the custom manager is being used.
        """

        self.assertIsInstance(Entity.objects, SearchManager)


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
