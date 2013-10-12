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


# Standard library imports.
from StringIO import StringIO
from zipfile import ZipFile, ZIP_DEFLATED

# Python third-party library imports.
import mock

# Django imports.
from django.core.urlresolvers import reverse
from django.http import Http404
from django.test import RequestFactory
from django.test import TestCase

# Application imports
from conntrackt.models import Project, Location, Entity, Interface, Communication

from conntrackt.views import IndexView
from conntrackt.views import entity_iptables, project_iptables, project_diagram

from conntrackt.views import ProjectView, ProjectCreateView, ProjectUpdateView, ProjectDeleteView
from conntrackt.views import LocationCreateView, LocationUpdateView, LocationDeleteView
from conntrackt.views import EntityView, EntityCreateView, EntityUpdateView, EntityDeleteView
from conntrackt.views import InterfaceCreateView, InterfaceUpdateView, InterfaceDeleteView
from conntrackt.views import CommunicationCreateView, CommunicationUpdateView, CommunicationDeleteView

# Test imports.
from .forms import FormWithWidgetCSSClassFormMixin, FormWithPlaceholderFormMixin
from .helpers import PermissionTestMixin, create_get_request, generate_get_response, FakeMessages
from .views import RedirectToNextMixinView
from .factories import setup_test_data


class IndexViewTest(PermissionTestMixin, TestCase):

    sufficient_permissions = ("view",)
    view_class = IndexView

    def setUp(self):
        """
        Set-up some test data.
        """

        setup_test_data()

    def test_context_no_projects(self):
        """
        Verifies that the context is properly set-up when the view is called and
        no projects are available.
        """

        Project.objects.all().delete()

        # Get the view.
        view = IndexView.as_view()

        # Get the response.
        response = generate_get_response(view)

        # Validate the response.
        self.assertQuerysetEqual(response.context_data["projects"], [])

    def test_context_no_locations(self):
        """
        Verifies that the context is properly set-up when the view is called and
        no locations are available.
        """

        Location.objects.all().delete()

        # Get the view.
        view = IndexView.as_view()

        # Get the response.
        response = generate_get_response(view)

        # Validate the response.
        self.assertQuerysetEqual(response.context_data["locations"], [])

    def test_context_projects(self):
        """
        Verifies that the context is properly set-up when the view is called and
        there's multiple projects available.
        """

        # Get the view.
        view = IndexView.as_view()

        # Get the response.
        response = generate_get_response(view)

        self.assertQuerysetEqual(response.context_data["projects"], ["<Project: Test Project 1>", "<Project: Test Project 2>"])

    def test_locations_available(self):
        """
        Verifies that the context is properly set-up when the view is called and
        there's multiple locationsg available.
        """

        # Get the view.
        view = IndexView.as_view()

        # Get the response.
        response = generate_get_response(view)

        # Validate the response.
        self.assertQuerysetEqual(response.context_data["locations"], ["<Location: Test Location 1>", "<Location: Test Location 2>"])


class ProjectViewTest(PermissionTestMixin, TestCase):

    sufficient_permissions = ("view",)
    permission_test_view_kwargs = {"pk": "1"}
    view_class = ProjectView

    def setUp(self):
        """
        Set-up some test data.
        """

        setup_test_data()

    def test_context(self):
        """
        Verifies that the context is properly set-up when the view is called.
        """

        # Get the view.
        view = ProjectView.as_view()

        # Get the response.
        response = generate_get_response(view, pk=1)

        # Fetch context data from response.
        location, entities = response.context_data["location_entities"][0]

        # Set-up expected context data values.
        expected_entities = ["<Entity: Test Entity 1 (Test Project 1 - Test Location 1)>",
                             "<Entity: Test Entity 2 (Test Project 1 - Test Location 1)>"]

        # Validate context data.
        self.assertEqual(location.name, "Test Location 1")
        self.assertQuerysetEqual(entities, expected_entities)

        # Fetch context data from response.
        location, entities = response.context_data["location_entities"][1]

        # Set-up expected context data values.
        expected_entities = ["<Entity: Test Entity 3 (Test Project 1 - Test Location 2)>",
                             "<Entity: Test Subnet 4 (Test Project 1 - Test Location 2)>"]

        # Validate context data.
        self.assertEqual(location.name, "Test Location 2")
        self.assertQuerysetEqual(entities, expected_entities)

        # Validate context data.
        self.assertEqual(str(response.context_data["project"]), "Test Project 1")


class EntityViewTest(PermissionTestMixin, TestCase):

    view_class = EntityView
    sufficient_permissions = ("view",)
    permission_test_view_kwargs = {"pk": "1"}

    def setUp(self):
        """
        Set-up some test data.
        """

        setup_test_data()

    def test_context(self):
        """
        Tests if the form comes pre-populated with proper content.
        """

        # Get the view.
        view = EntityView.as_view()

        # Get the response.
        response = generate_get_response(view, pk=1)

        # Set-up expected context data.
        expected_entity = Entity.objects.get(pk=1)

        expected_incoming_communications = ["<Communication: Test Entity 2 -> Test Entity 1 (TCP:22)>",
                                            "<Communication: Test Entity 2 -> Test Entity 1 (ICMP:8)>",
                                            "<Communication: Test Entity 3 -> Test Entity 1 (TCP:3306)>",
                                            "<Communication: Test Subnet 4 -> Test Entity 1 (TCP:22)>"]

        expected_outgoing_communications = ["<Communication: Test Entity 1 -> Test Entity 2 (UDP:123)>",
                                            "<Communication: Test Entity 1 -> Test Entity 3 (UDP:53)>"]

        expected_interfaces = ["<Interface: Test Entity 1 (192.168.1.1)>"]

        # Validate the response.
        self.assertQuerysetEqual(response.context_data["interfaces"], expected_interfaces)
        self.assertQuerysetEqual(response.context_data["incoming_communications"], expected_incoming_communications)
        self.assertQuerysetEqual(response.context_data["outgoing_communications"], expected_outgoing_communications)
        self.assertEqual(response.context_data["entity"], expected_entity)
        self.assertTrue("entity_iptables" in response.context_data)


class EntityIptablesTest(PermissionTestMixin, TestCase):

    view_function = staticmethod(entity_iptables)
    sufficient_permissions = ("view",)
    permission_test_view_kwargs = {"pk": "1"}

    def setUp(self):
        """
        Set-up some test data.
        """

        setup_test_data()

    def test_invalid_entity(self):
        """
        Tests if a 404 is returned if no entity was found (invalid ID).
        """

        # Set-up a request.
        request = create_get_request()

        # Get the view.
        view = entity_iptables

        # Validate the response.
        self.assertRaises(Http404, view, request, pk=200)

    def test_content_type(self):
        """
        Test if correct content type is being returned by the response.
        """

        # Get the view.
        view = entity_iptables

        # Get the response.
        response = generate_get_response(view, pk=1)

        self.assertEqual(response['Content-Type'], "text/plain")

    def test_content_disposition(self):
        """
        Test if the correct content disposition has been set.
        """

        # Get the view.
        view = entity_iptables

        # Get the response.
        response = generate_get_response(view, pk=1)

        self.assertEqual(response['Content-Disposition'], "attachment; filename=test_entity_1-iptables.conf")

    def test_content(self):
        """
        Tests content produced by the view.
        """

        # Get the view.
        view = entity_iptables

        # Get the response.
        response = generate_get_response(view, pk=1)

        self.assertContains(response, ":INPUT")
        self.assertContains(response, ":OUTPUT")
        self.assertContains(response, ":FORWARD")


class ProjectIptablesTest(PermissionTestMixin, TestCase):

    view_function = staticmethod(project_iptables)
    sufficient_permissions = ("view",)
    permission_test_view_kwargs = {"project_id": 1}

    def setUp(self):
        """
        Set-up some test data.
        """

        setup_test_data()

    def test_invalid_project(self):
        """
        Tests if a 404 is returned if no project was found (invalid ID).
        """

        # Set-up a request.
        request = create_get_request()

        # Get the view.
        view = project_iptables

        # Request iptables for whole project.
        self.assertRaises(Http404, view, request, 200)
        # Request iptables for project location
        self.assertRaises(Http404, view, request, 200, 1)

    def test_invalid_location(self):
        """
        Tests if a 404 is returned if no location was found (invalid ID).
        """

        # Set-up a request.
        request = create_get_request()

        # Get the view.
        view = project_iptables

        # Request iptables for project location
        self.assertRaises(Http404, view, request, 1, 200)

    def test_content_type(self):
        """
        Test if correct content type is being returned by the response.
        """

        # Get the view.
        view = project_iptables

        # Get the response.
        response = generate_get_response(view, None, 1)

        # Validate the response.
        self.assertEqual(response['Content-Type'], "application/zip")

    def test_content_disposition(self):
        """
        Test if the correct content disposition has been set.
        """

        # Get the view.
        view = project_iptables

        # Get the response.
        response = generate_get_response(view, None, 1)
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="test_project_1-iptables.zip"')

        response = generate_get_response(view, None, 1, 1)
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="test_project_1-test_location_1-iptables.zip"')

    def test_content_project(self):
        """
        Verifies that the content is properly generated when the view is called
        for an entire project.
        """

        # Get the view.
        view = project_iptables

        # Get the response.
        response = generate_get_response(project_iptables, None, 1)

        buff = StringIO(response.content)

        zipped_iptables = ZipFile(buff, "r", ZIP_DEFLATED)
        expected_zip_files = ["test_entity_1-iptables.conf",
                              "test_entity_2-iptables.conf",
                              "test_entity_3-iptables.conf",
                              "test_subnet_4-iptables.conf"]

        self.assertEqual(len(zipped_iptables.namelist()), 4)
        self.assertEqual(zipped_iptables.namelist(), expected_zip_files)

        for filename in expected_zip_files:
            iptables_file = zipped_iptables.read(filename)
            self.assertIn(":INPUT", iptables_file)
            self.assertIn(":OUTPUT", iptables_file)
            self.assertIn(":FORWARD", iptables_file)

        zipped_iptables.close()

    def test_content_location(self):
        """
        Verifies that the content is properly generated when the view is called
        for an entire project.
        """

        # Get the view.
        view = project_iptables

        # Get the response.
        response = generate_get_response(project_iptables, None, 1, 1)

        buff = StringIO(response.content)

        zipped_iptables = ZipFile(buff, "r", ZIP_DEFLATED)
        expected_zip_files = ["test_entity_1-iptables.conf",
                              "test_entity_2-iptables.conf"]

        self.assertEqual(len(zipped_iptables.namelist()), 2)
        self.assertEqual(zipped_iptables.namelist(), expected_zip_files)

        for filename in expected_zip_files:
            iptables_file = zipped_iptables.read(filename)
            self.assertIn(":INPUT", iptables_file)
            self.assertIn(":OUTPUT", iptables_file)
            self.assertIn(":FORWARD", iptables_file)

        zipped_iptables.close()


class ProjectCreateViewTest(PermissionTestMixin, TestCase):

    view_class = ProjectCreateView
    sufficient_permissions = ("add_project",)


class ProjectUpdateViewTest(PermissionTestMixin, TestCase):

    view_class = ProjectUpdateView
    sufficient_permissions = ("change_project",)
    permission_test_view_kwargs = {"pk": 1}

    def setUp(self):
        """
        Set-up some test data.
        """

        setup_test_data()

    def test_context(self):
        """
        Verifies that the context is properly set-up when the view is called for
        specific project.
        """

        # Get the view.
        view = ProjectUpdateView.as_view()

        # Get the response.
        response = generate_get_response(view, None, pk=1)

        self.assertEqual(response.context_data["project"].name, "Test Project 1")
        self.assertEqual(response.context_data["headline"], "Update project Test Project 1")


class ProjectDeleteViewTest(PermissionTestMixin, TestCase):

    view_class = ProjectDeleteView
    sufficient_permissions = ("delete_project",)
    permission_test_view_kwargs = {"pk": "1"}

    def setUp(self):
        """
        Set-up some test data.
        """

        setup_test_data()

    def test_context(self):
        """
        Verifies that the context is properly set-up when the view is called for
        specific project.
        """

        # Get the expected project.
        project = Project.objects.get(pk=1)

        # Get the view.
        view = ProjectDeleteView.as_view()

        # Get the response.
        response = generate_get_response(view, None, pk=1)

        self.assertEqual(response.context_data["project"], project)
        self.assertEqual(response.context_data["headline"], "Delete project Test Project 1")

    def test_message(self):
        """
        Tests if the message gets added when the project is deleted.
        """

        # Get the view.
        view = ProjectDeleteView.as_view()

        # Generate the request.
        request = RequestFactory().post("/fake-path/")
        request.user = mock.Mock()
        request._dont_enforce_csrf_checks = True
        request._messages = FakeMessages()

        # Get the response.
        response = view(request, pk=1)

        self.assertIn("Project Test Project 1 has been removed.", request._messages.messages)


class LocationCreateViewTest(PermissionTestMixin, TestCase):

    view_class = LocationCreateView
    sufficient_permissions = ("add_location",)


class LocationUpdateViewTest(PermissionTestMixin, TestCase):

    view_class = LocationUpdateView
    sufficient_permissions = ("change_location",)
    permission_test_view_kwargs = {"pk": 1}

    def setUp(self):
        """
        Set-up some test data.
        """

        setup_test_data()

    def test_context(self):
        """
        Verifies that the context is properly set-up when the view is called for
        specific location.
        """

        # Get the view.
        view = LocationUpdateView.as_view()

        # Get the response.
        response = generate_get_response(view, None, pk=1)

        self.assertEqual(response.context_data["location"].name, "Test Location 1")
        self.assertEqual(response.context_data["headline"], "Update location Test Location 1")


class LocationDeleteViewTest(PermissionTestMixin, TestCase):

    view_class = LocationDeleteView
    sufficient_permissions = ("delete_location",)
    permission_test_view_kwargs = {"pk": "1"}

    def setUp(self):
        """
        Set-up some test data.
        """

        setup_test_data()

    def test_context(self):
        """
        Verifies that the context is properly set-up when the view is called for
        specific location.
        """

        # Get the expected location.
        location = Location.objects.get(pk=1)

        # Get the view.
        view = LocationDeleteView.as_view()

        # Get the response.
        response = generate_get_response(view, None, pk=1)

        self.assertEqual(response.context_data["location"], location)
        self.assertEqual(response.context_data["headline"], "Delete location Test Location 1")

    def test_message(self):
        """
        Tests if the message gets added when the location is deleted.
        """

        # Get the view.
        view = LocationDeleteView.as_view()

        # Generate the request.
        request = RequestFactory().post("/fake-path/")
        request.user = mock.Mock()
        request._dont_enforce_csrf_checks = True

        request._messages = FakeMessages()

        # Get the response.
        response = view(request, pk=1)

        self.assertIn("Location Test Location 1 has been removed.", request._messages.messages)


class EntityCreateViewTest(PermissionTestMixin, TestCase):

    view_class = EntityCreateView
    sufficient_permissions = ("add_entity",)

    def setUp(self):
        """
        Sets-up some data necessary for testing.
        """

        # Set-up some data for testing.
        Project.objects.create(name="Test Project 1", description="This is test project 1.")
        Project.objects.create(name="Test Project 2", description="This is test project 2.")
        Location.objects.create(name="Test Location 1", description="This is test location 1.")
        Location.objects.create(name="Test Location 2", description="This is test location 2.")

    def test_form_project_limit(self):
        """
        Tests if the queryset is properly limitted to specific project if GET
        parameters is passed.
        """

        # Set-up the view.
        view = EntityCreateView()
        view.request = RequestFactory().get("/fake-path?project=1")
        view.object = None

        # Get the form.
        form = view.get_form(view.get_form_class())

        self.assertQuerysetEqual(form.fields["project"].queryset, ["<Project: Test Project 1>"])

    def test_form_location_limit(self):
        """
        Tests if the queryset is properly limitted to specific location if GET
        parameters is passed.
        """

        # Set-up the view.
        view = EntityCreateView()
        view.request = RequestFactory().get("/fake-path?location=1")
        view.object = None

        # Get the form.
        form = view.get_form(view.get_form_class())

        self.assertQuerysetEqual(form.fields["location"].queryset, ["<Location: Test Location 1>"])

    def test_initial_project(self):
        """
        Tests if the choice field for project is defaulted to project passed as
        part of GET parameters.
        """

        view = EntityCreateView()
        view.request = RequestFactory().get("/fake-path?project=1")
        view.object = None

        initial = view.get_initial()

        self.assertDictContainsSubset({"project": "1"}, initial)

    def test_initial_location(self):
        """
        Tests if the choice field for location is defaulted to location passed
        as part of GET parameters.
        """

        view = EntityCreateView()
        view.request = RequestFactory().get("/fake-path?location=1")
        view.object = None

        initial = view.get_initial()

        self.assertDictContainsSubset({"location": "1"}, initial)


class EntityDeleteViewTest(PermissionTestMixin, TestCase):

    view_class = EntityDeleteView
    sufficient_permissions = ("delete_entity",)
    permission_test_view_kwargs = {"pk": 1}

    def setUp(self):
        """
        Set-up some test data.
        """

        setup_test_data()

    def test_context(self):
        """
        Verifies that the context is properly set-up when the view is called for
        specific entity.
        """

        # Get the expected entity.
        entity = Entity.objects.get(pk=1)

        # Get the view.
        view = EntityDeleteView.as_view()

        # Get the response.
        response = generate_get_response(view, None, pk=1)

        self.assertEqual(response.context_data["entity"], entity)
        self.assertEqual(response.context_data["headline"], "Delete entity Test Entity 1")

    def test_message(self):
        """
        Tests if the message gets added when the entity is deleted.
        """

        # Get the view.
        view = EntityDeleteView.as_view()

        # Generate the request.
        request = RequestFactory().post("/fake-path/")
        request.user = mock.Mock()
        request._dont_enforce_csrf_checks = True

        request._messages = FakeMessages()

        # Get the response.
        response = view(request, pk=1)

        self.assertIn("Entity Test Entity 1 has been removed.", request._messages.messages)

    def test_success_url(self):
        """
        Validate that the success URL is set properly after delete.
        """

        # Get the view.
        view = EntityDeleteView.as_view()

        # Generate the request
        request = RequestFactory().post("/fake-path/")
        request.user = mock.Mock()
        request._dont_enforce_csrf_checks = True
        request._messages = FakeMessages()

        # Get the response.
        response = view(request, pk=1)

        self.assertEqual(response["Location"], reverse("project", args=(1,)))


class EntityUpdateViewTest(PermissionTestMixin, TestCase):

    view_class = EntityUpdateView
    sufficient_permissions = ("change_entity",)
    permission_test_view_kwargs = {"pk": 1}

    def setUp(self):
        """
        Set-up some test data.
        """

        setup_test_data()

    def test_context(self):
        """
        Verifies that the context is properly set-up when the view is called for
        specific entity.
        """

        # Get the view.
        view = EntityUpdateView.as_view()

        # Get the response.
        response = generate_get_response(view, None, pk=1)

        self.assertEqual(response.context_data["entity"].name, "Test Entity 1")
        self.assertEqual(response.context_data["headline"], "Update entity Test Entity 1")


class InterfaceCreateViewTest(PermissionTestMixin, TestCase):

    view_class = InterfaceCreateView
    sufficient_permissions = ("add_interface",)

    def setUp(self):
        """
        Sets-up some data necessary for testing.
        """

        # Set-up some data for testing.
        project = Project.objects.create(name="Test Project", description="This is test project.")
        location = Location.objects.create(name="Test Location", description="This is test location.")
        Entity.objects.create(name="Test Entity 1", description="This is test entity 1.", project=project, location=location)
        Entity.objects.create(name="Test Entity 2", description="This is test entity 2.", project=project, location=location)

    def test_form_entity_limit(self):
        """
        Tests if the queryset is properly limitted to specific entity if GET
        parameter is passed.
        """

        # Set-up the view.
        view = InterfaceCreateView()
        view.request = RequestFactory().get("/fake-path?entity=1")
        view.object = None

        # Get the form.
        form = view.get_form(view.get_form_class())

        self.assertQuerysetEqual(form.fields["entity"].queryset, ["<Entity: Test Entity 1 (Test Project - Test Location)>"])

    def test_initial_project(self):
        """
        Tests if the choice field for entity is defaulted to entity passed as
        part of GET parameters.
        """

        view = InterfaceCreateView()
        view.request = RequestFactory().get("/fake-path?entity=1")
        view.object = None

        initial = view.get_initial()

        self.assertDictContainsSubset({"entity": "1"}, initial)

    def test_success_url(self):
        """
        Validate that the success URL is set properly after interface is
        created.
        """

        # Get the view.
        view = InterfaceCreateView.as_view()

        # Generate the request.
        post_data = {"name": "eth0", "description": "Main interface.",
                     "entity": "1", "address": "192.168.1.1",
                     "netmask": "255.255.255.255"}
        request = RequestFactory().post("/fake-path/", data=post_data)
        request.user = mock.Mock()
        request._dont_enforce_csrf_checks = True

        # Get the response.
        response = view(request, pk=1)

        self.assertEqual(response["Location"], reverse("entity", args=(1,)))
        self.assertEqual(response.status_code, 302)


class InterfaceUpdateViewTest(PermissionTestMixin, TestCase):

    view_class = InterfaceUpdateView
    sufficient_permissions = ("change_interface",)
    permission_test_view_kwargs = {"pk": 1}

    def setUp(self):
        """
        Set-up some test data.
        """

        setup_test_data()

    def test_context(self):
        """
        Verifies that the context is properly set-up when the view is called for
        specific entity.
        """

        # Get the view.
        view = InterfaceUpdateView.as_view()

        # Get the response.
        response = generate_get_response(view, None, pk=1)

        # Set-up expected interface.
        interface = Interface.objects.get(pk=1)

        self.assertEqual(response.context_data["interface"], interface)
        self.assertEqual(response.context_data["headline"], "Update interface eth0")

    def test_form_entity_limit(self):
        """
        Tests if the queryset is properly limitted to specific project's
        entities.
        """

        # Set-up the view.
        view = InterfaceUpdateView()
        view.request = RequestFactory().get("/fake-path/1")
        view.object = Interface.objects.get(pk=1)

        # Get the form.
        form = view.get_form(view.get_form_class())

        expected_entities = ["<Entity: Test Entity 1 (Test Project 1 - Test Location 1)>",
                             "<Entity: Test Entity 2 (Test Project 1 - Test Location 1)>",
                             "<Entity: Test Entity 3 (Test Project 1 - Test Location 2)>",
                             "<Entity: Test Subnet 4 (Test Project 1 - Test Location 2)>"]

        self.assertQuerysetEqual(form.fields["entity"].queryset, expected_entities)

    def test_success_url(self):
        """
        Validate that the success URL is set properly after update.
        """

        # Get the view.
        view = InterfaceUpdateView.as_view()

        # Get the interface object.
        interface = Interface.objects.get(pk=1)

        # Generate the request.
        post_data = {"name": interface.name, "description": interface.name,
                     "entity": "1", "address": "192.168.1.1",
                     "netmask": "255.255.255.255"}
        request = RequestFactory().post("/fake-path/", data=post_data)
        request.user = mock.Mock()
        request._dont_enforce_csrf_checks = True

        # Get the response.
        response = view(request, pk=1)

        self.assertEqual(response["Location"], reverse("entity", args=(1,)))
        self.assertEqual(response.status_code, 302)


class InterfaceDeleteViewTest(PermissionTestMixin, TestCase):

    view_class = InterfaceDeleteView
    sufficient_permissions = ("delete_interface",)
    permission_test_view_kwargs = {"pk": 1}

    def setUp(self):
        """
        Set-up some test data.
        """

        setup_test_data()

    def test_context(self):
        """
        Verifies that the context is properly set-up when the view is called for
        specific interface.
        """

        # Get the expected entity.
        interface = Interface.objects.get(pk=1)

        # Get the view.
        view = InterfaceDeleteView.as_view()

        # Get the response.
        response = generate_get_response(view, None, pk=1)

        self.assertEqual(response.context_data["interface"], interface)
        self.assertEqual(response.context_data["headline"], "Delete interface eth0")

    def test_message(self):
        """
        Tests if the message gets added when the interface is deleted.
        """

        # Get the view.
        view = InterfaceDeleteView.as_view()

        # Generate the request.
        request = RequestFactory().post("/fake-path/")
        request.user = mock.Mock()
        request._dont_enforce_csrf_checks = True

        request._messages = FakeMessages()

        # Get the response.
        response = view(request, pk=1)

        self.assertIn("Interface eth0 has been removed.", request._messages.messages)

    def test_success_url(self):
        """
        Validate that the success URL is set properly after delete.
        """

        # Get the view.
        view = InterfaceDeleteView.as_view()

        # Generate the request
        request = RequestFactory().post("/fake-path/")
        request.user = mock.Mock()
        request._dont_enforce_csrf_checks = True
        request._messages = FakeMessages()

        # Get the response.
        response = view(request, pk=1)

        self.assertEqual(response["Location"], reverse("entity", args=(1,)))


class CommunicationCreateViewTest(PermissionTestMixin, TestCase):

    view_class = CommunicationCreateView
    sufficient_permissions = ("add_communication",)

    def setUp(self):
        """
        Sets-up some data necessary for testing.
        """

        # Set-up some data for testing.
        project1 = Project.objects.create(name="Test Project 1", description="This is test project 1.")
        project2 = Project.objects.create(name="Test Project 2", description="This is test project 2.")
        location = Location.objects.create(name="Test Location", description="This is test location.")
        entity1 = Entity.objects.create(name="Test Entity 1", description="This is test entity 1.", project=project1, location=location)
        entity2 = Entity.objects.create(name="Test Entity 2", description="This is test entity 2.", project=project1, location=location)
        entity3 = Entity.objects.create(name="Test Entity 3", description="This is test entity 3.", project=project2, location=location)
        Interface.objects.create(name="eth0", description="Main interface", entity=entity1, address="192.168.1.1", netmask="255.255.255.255")
        Interface.objects.create(name="eth0", description="Main interface", entity=entity2, address="192.168.1.2", netmask="255.255.255.255")
        Interface.objects.create(name="eth0", description="Main interface", entity=entity3, address="192.168.1.3", netmask="255.255.255.255")

    def test_interface_limit_from_entity(self):
        """
        Tests if the queryset is properly limitted if GET parameter is passed.
        """

        # Set-up the view.
        view = CommunicationCreateView()
        view.request = RequestFactory().get("/fake-path?from_entity=1")
        view.object = None

        # Get the form.
        form = view.get_form(view.get_form_class())

        # Set-up expected interfaces.
        expected_interfaces = ["<Interface: Test Entity 1 (192.168.1.1)>",
                               "<Interface: Test Entity 2 (192.168.1.2)>"]

        self.assertQuerysetEqual(form.fields["source"].queryset, expected_interfaces)
        self.assertQuerysetEqual(form.fields["destination"].queryset, expected_interfaces)

    def test_interface_limit_to_entity(self):
        """
        Tests if the queryset is properly limitted if GET parameter is passed.
        """

        # Set-up the view.
        view = CommunicationCreateView()
        view.request = RequestFactory().get("/fake-path?to_entity=1")
        view.object = None

        # Get the form.
        form = view.get_form(view.get_form_class())

        # Set-up expected interfaces.
        expected_interfaces = ["<Interface: Test Entity 1 (192.168.1.1)>",
                               "<Interface: Test Entity 2 (192.168.1.2)>"]

        self.assertQuerysetEqual(form.fields["source"].queryset, expected_interfaces)
        self.assertQuerysetEqual(form.fields["destination"].queryset, expected_interfaces)

    def test_interface_limit_project(self):
        """
        Tests if the queryset is properly limitted if GET parameter is passed.
        """

        # Set-up the view.
        view = CommunicationCreateView()
        view.request = RequestFactory().get("/fake-path?project=1")
        view.object = None

        # Get the form.
        form = view.get_form(view.get_form_class())

        # Set-up expected interfaces.
        expected_interfaces = ["<Interface: Test Entity 1 (192.168.1.1)>",
                               "<Interface: Test Entity 2 (192.168.1.2)>"]

        self.assertQuerysetEqual(form.fields["source"].queryset, expected_interfaces)
        self.assertQuerysetEqual(form.fields["destination"].queryset, expected_interfaces)

    def test_initial_from_entity(self):
        """
        Tests if the choice field for interface is defaulted to first interface
        of entity passed as part of GET parameters.
        """

        # Set-up the view.
        view = CommunicationCreateView()
        view.request = RequestFactory().get("/fake-path?from_entity=1")
        view.object = None

        # Get the expected interface ID.
        interface = Entity.objects.get(pk=1).interface_set.all()[0]

        # Fetch the initial values.
        initial = view.get_initial()

        self.assertDictContainsSubset({"source": interface.pk}, initial)

    def test_initial_to_entity(self):
        """
        Tests if the choice field for interface is defaulted to first interface
        of entity passed as part of GET parameters.
        """

        # Set-up the view.
        view = CommunicationCreateView()
        view.request = RequestFactory().get("/fake-path?to_entity=1")
        view.object = None

        # Get the expected interface ID.
        interface = Entity.objects.get(pk=1).interface_set.all()[0]

        # Fetch the initial value.
        initial = view.get_initial()

        self.assertDictContainsSubset({"destination": interface.pk}, initial)

    def test_initial_invalid_from_entity(self):
        """
        Tests if the choice fields for source and destination interfaces are not
        defaulted in case invalid entity ID is passed as GET parameter.
        """

        # Set-up the view.
        view = CommunicationCreateView()
        view.request = RequestFactory().get("/fake-path?from_entity=10")
        view.object = None

        # Get the initial values.
        initial = view.get_initial()

        self.assertEqual(len(initial), 0)

    def test_initial_invalid_to_entity(self):
        """
        Tests if the choice fields for source and destination interfaces are not
        defaulted in case invalid entity ID is passed as GET parameter.
        """

        # Set-up the view.
        view = CommunicationCreateView()
        view.request = RequestFactory().get("/fake-path?to_entity=10")
        view.object = None

        # Get the initial values.
        initial = view.get_initial()

        self.assertEqual(len(initial), 0)

    def test_initial_invalid_project(self):
        """
        Tests if the choice fields for source and destination interfaces are not
        defaulted in case invalid project ID is passed as GET parameter.
        """

        # Set-up the view.
        view = CommunicationCreateView()
        view.request = RequestFactory().get("/fake-path?project=10")
        view.object = None

        # Get the initial values.
        initial = view.get_initial()

        self.assertEqual(len(initial), 0)

    def test_success_url_next(self):
        """
        Validate that the success URL is set properly after communication is
        created if "next" GET parameter is provided.
        """

        # Get the view.
        view = CommunicationCreateView.as_view()

        # Generate the request.
        source = Interface.objects.get(pk=1)
        destination = Interface.objects.get(pk=2)
        post_data = {"source": source.pk,
                     "destination": destination.pk,
                     "protocol": "TCP",
                     "port": "22",
                     "description": "SSH."}
        request = RequestFactory().post("/fake-path?next=/next-page", data=post_data)
        request.user = mock.Mock()
        request._dont_enforce_csrf_checks = True

        # Get the response.
        response = view(request)

        self.assertEqual(response["Location"], "/next-page")
        self.assertEqual(response.status_code, 302)

    def test_success_url_no_next(self):
        """
        Validate that the success URL is set properly after communication is
        created if no "next" GET parameter is provided.
        """

        # Get the view.
        view = CommunicationCreateView.as_view()

        # Generate the request.
        source = Interface.objects.get(pk=1)
        destination = Interface.objects.get(pk=2)
        post_data = {"source": source.pk,
                     "destination": destination.pk,
                     "protocol": "TCP",
                     "port": "22",
                     "description": "SSH."}
        request = RequestFactory().post("/fake-path", data=post_data)
        request.user = mock.Mock()
        request._dont_enforce_csrf_checks = True

        # Get the response.
        response = view(request)

        self.assertEqual(response["Location"], reverse("project", args=(1,)))
        self.assertEqual(response.status_code, 302)


class CommunicationUpdateViewTest(PermissionTestMixin, TestCase):

    view_class = CommunicationUpdateView
    sufficient_permissions = ("change_communication",)
    permission_test_view_kwargs = {"pk": 1}

    def setUp(self):
        """
        Set-up some test data.
        """

        setup_test_data()

    def test_context(self):
        """
        Verifies that the context is properly set-up.
        """

        # Get the view.
        view = CommunicationUpdateView.as_view()

        # Get the response.
        response = generate_get_response(view, None, pk=1)

        # Set-up expected interface.
        communication = Communication.objects.get(pk=1)

        self.assertEqual(response.context_data["communication"], communication)
        self.assertEqual(response.context_data["headline"], "Update communication Test Entity 2 -> Test Entity 1 (TCP:22)")

    def test_form_interface_limit(self):
        """
        Tests if the queryset is properly limitted to specific project's
        entity interfaces.
        """

        # Set-up the view.
        view = CommunicationUpdateView()
        view.request = RequestFactory().get("/fake-path/1")
        view.object = Communication.objects.get(pk=1)

        # Get the form.
        form = view.get_form(view.get_form_class())

        expected_interfaces = ["<Interface: Test Entity 1 (192.168.1.1)>",
                               "<Interface: Test Entity 2 (192.168.1.2)>",
                               "<Interface: Test Entity 3 (192.168.1.3)>",
                               "<Interface: Test Subnet 4 (10.10.4.0/255.255.255.0)>"]

        self.assertQuerysetEqual(form.fields["source"].queryset, expected_interfaces)
        self.assertQuerysetEqual(form.fields["destination"].queryset, expected_interfaces)

    def test_success_url_next(self):
        """
        Validate that the success URL is set properly after update if GET
        parameter is passed.
        """

        # Get the view.
        view = CommunicationUpdateView.as_view()

        # Get the communication object.
        communication = Communication.objects.get(pk=1)

        # Generate the request.
        post_data = {"source": communication.source.pk,
                     "destination": communication.destination.pk,
                     "protocol": communication.protocol,
                     "port": communication.port}
        request = RequestFactory().post("/fake-path?next=/next-page", data=post_data)
        request.user = mock.Mock()
        request._dont_enforce_csrf_checks = True

        # Get the response.
        response = view(request, pk=1)

        self.assertEqual(response["Location"], "/next-page")
        self.assertEqual(response.status_code, 302)

    def test_success_url_no_next(self):
        """
        Validate that the success URL is set properly after communication is
        created if no "next" GET parameter is provided.
        """

        # Get the view.
        view = CommunicationUpdateView.as_view()

        # Get the communication object.
        communication = Communication.objects.get(pk=1)

        # Generate the request.
        post_data = {"source": communication.source.pk,
                     "destination": communication.destination.pk,
                     "protocol": communication.protocol,
                     "port": communication.port}
        request = RequestFactory().post("/fake-path/", data=post_data)
        request.user = mock.Mock()
        request._dont_enforce_csrf_checks = True

        # Get the response.
        response = view(request, pk=1)

        self.assertEqual(response["Location"], reverse("project", args=(communication.source.entity.project.id,)))
        self.assertEqual(response.status_code, 302)


class CommunicationDeleteViewTest(PermissionTestMixin, TestCase):

    view_class = CommunicationDeleteView
    sufficient_permissions = ("delete_communication",)
    permission_test_view_kwargs = {"pk": 1}

    def setUp(self):
        """
        Set-up some test data.
        """

        setup_test_data()

    def test_context(self):
        """
        Verifies that the context is properly set-up when the view is called for
        specific communication.
        """

        # Get the expected entity.
        communication = Communication.objects.get(pk=1)

        # Get the view.
        view = CommunicationDeleteView.as_view()

        # Get the response.
        response = generate_get_response(view, None, pk=1)

        self.assertEqual(response.context_data["communication"], communication)
        self.assertEqual(response.context_data["headline"], "Delete communication Test Entity 2 -> Test Entity 1 (TCP:22)")

    def test_message(self):
        """
        Tests if the message gets added when the communication is deleted.
        """

        # Get the view.
        view = CommunicationDeleteView.as_view()

        # Generate the request.
        request = RequestFactory().post("/fake-path/")
        request.user = mock.Mock()
        request._dont_enforce_csrf_checks = True

        request._messages = FakeMessages()

        # Get the response.
        response = view(request, pk=1)

        self.assertIn("Communication Test Entity 2 -> Test Entity 1 (TCP:22) has been removed.", request._messages.messages)

    def test_success_url_from_entity(self):
        """
        Validate that the success URL is set properly after delete.
        """

        # Get the view.
        view = CommunicationDeleteView.as_view()

        # Generate the request
        request = RequestFactory().post("/fake-path?from_entity=1")
        request.user = mock.Mock()
        request._dont_enforce_csrf_checks = True
        request._messages = FakeMessages()

        # Get the response.
        response = view(request, pk=1)

        self.assertEqual(response["Location"], reverse("entity", args=(1,)))

    def test_success_url_to_entity(self):
        """
        Validate that the success URL is set properly after delete.
        """

        # Get the view.
        view = CommunicationDeleteView.as_view()

        # Generate the request
        request = RequestFactory().post("/fake-path?to_entity=1")
        request.user = mock.Mock()
        request._dont_enforce_csrf_checks = True
        request._messages = FakeMessages()

        # Get the response.
        response = view(request, pk=1)

        self.assertEqual(response["Location"], reverse("entity", args=(1,)))

    def test_success_url_no_entity(self):
        """
        Validate that the success URL is set properly after delete.
        """

        # Get the view.
        view = CommunicationDeleteView.as_view()

        # Get the communication object.
        communication = Communication.objects.get(pk=1)

        # Generate the request
        request = RequestFactory().post("/fake-path")
        request.user = mock.Mock()
        request._dont_enforce_csrf_checks = True
        request._messages = FakeMessages()

        # Get the response.
        response = view(request, pk=1)

        self.assertEqual(response["Location"], reverse("entity", args=(communication.source.entity.pk,)))


class ProjectDiagramTest(PermissionTestMixin, TestCase):

    view_function = staticmethod(project_diagram)
    sufficient_permissions = ("view",)
    permission_test_view_kwargs = {"pk": "1"}

    def setUp(self):
        """
        Set-up some test data.
        """

        setup_test_data()

    def test_invalid_project(self):
        """
        Tests if a 404 is returned if no project was found (invalid ID).
        """

        # Set-up a request.
        request = create_get_request()

        # Get the view.
        view = project_diagram

        # Validate the response.
        self.assertRaises(Http404, view, request, pk=200)

    def test_content_type(self):
        """
        Test if correct content type is being returned by the response.
        """

        # Get the view.
        view = project_diagram

        # Get the response.
        response = generate_get_response(view, pk=1)

        self.assertEqual(response['Content-Type'], "image/svg+xml")

    def test_content(self):
        """
        Tests content produced by the view.
        """

        # Get the view.
        view = project_diagram

        # Get the response.
        response = generate_get_response(view, pk=1)

        self.assertContains(response, '"-//W3C//DTD SVG 1.1//EN"')
        self.assertContains(response, "Test Project 1")


class RedirectToNextMixinTest(TestCase):

    def test_request_with_next(self):
        """
        Test if the get_success_url returns correct URL if "next" is present in
        request's GET parameters.
        """

        # Generate the request.
        request = RequestFactory().post("/fake-path?next=/next")

        # Initialise the pseudo-view.
        view = RedirectToNextMixinView(request)

        self.assertEqual("/next", view.get_success_url())

    def test_request_without_next(self):
        """
        Test if the get_success_url returns correct URL if "next" is not present
        in request's GET parameters.
        """

        # Generate the request.
        request = RequestFactory().post("/fake-path")

        # Initialise the pseudo-view.
        view = RedirectToNextMixinView(request)

        self.assertEqual("/STATIC", view.get_success_url())

    def test_request_custom_parameter_name(self):
        """
        Test if the mixin honours the custom parameter name.
        """

        # Generate the request.
        request = RequestFactory().post("/fake-path?custom=/next")

        # Initialise the pseudo-view.
        view = RedirectToNextMixinView(request)
        view.next_parameter = "custom"

        self.assertEqual("/next", view.get_success_url())
