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
from django.conf.urls import patterns, url
from django.contrib.auth.views import login, logout

# Application imports.
from .views import IndexView, EntityView, entity_iptables, project_iptables, project_diagram
from .views import ProjectView, ProjectCreateView, ProjectUpdateView, ProjectDeleteView
from .views import LocationCreateView, LocationUpdateView, LocationDeleteView
from .views import EntityCreateView, EntityUpdateView, EntityDeleteView
from .views import InterfaceCreateView, InterfaceUpdateView, InterfaceDeleteView
from .views import CommunicationCreateView, CommunicationUpdateView, CommunicationDeleteView


urlpatterns = patterns(
    'conntrackt.views',
    # Homepage/index view.
    url(r'^$', IndexView.as_view(), name="index"),

    # View for showing information about a project.
    url(r'^project/(?P<pk>\d+)/$', ProjectView.as_view(),
        name='project'),
    # View for creating a new project.
    url(r'^project/add/$', ProjectCreateView.as_view(), name="project_create"),
    # View for updating an existing project.
    url(r'^project/(?P<pk>\d+)/edit/$', ProjectUpdateView.as_view(), name="project_update"),
    # View for deleting a project.
    url(r'^project/(?P<pk>\d+)/remove/$', ProjectDeleteView.as_view(), name="project_delete"),

    # View for creating a new location.
    url(r'^location/add/$', LocationCreateView.as_view(), name="location_create"),
    # View for updating an existing location.
    url(r'^location/(?P<pk>\d+)/edit/$', LocationUpdateView.as_view(), name="location_update"),
    # View for deleting a location.
    url(r'^location/(?P<pk>\d+)/remove/$', LocationDeleteView.as_view(), name="location_delete"),

    # View for showing information about an entity.
    url(r'^entity/(?P<pk>\d+)/$', EntityView.as_view(),
        name='entity'),
    # View for creating a new entity.
    url(r'^entity/add/$', EntityCreateView.as_view(), name="entity_create"),
    # View for updating an existing entity.
    url(r'^entity/(?P<pk>\d+)/edit/$', EntityUpdateView.as_view(), name="entity_update"),
    # View for deleting an entity.
    url(r'^entity/(?P<pk>\d+)/remove/$', EntityDeleteView.as_view(), name="entity_delete"),

    # View for creating a new interface.
    url(r'^interface/add/$', InterfaceCreateView.as_view(), name="interface_create"),
    # View for updating an existing interface.
    url(r'^interface/(?P<pk>\d+)/edit/$', InterfaceUpdateView.as_view(), name="interface_update"),
    # View for deleting an interface.
    url(r'^interface/(?P<pk>\d+)/remove/$', InterfaceDeleteView.as_view(), name="interface_delete"),

    # View for creating a new communucation.
    url(r'^communication/add/$', CommunicationCreateView.as_view(), name="communication_create"),
    # View for updating an existing communication.
    url(r'^communication/(?P<pk>\d+)/edit/$', CommunicationUpdateView.as_view(), name="communication_update"),
    # View for deleting a communication.
    url(r'^communication/(?P<pk>\d+)/remove/$', CommunicationDeleteView.as_view(), name="communication_delete"),

    # View for rendering iptables rules for a specific entity.
    url(r'^entity/(?P<pk>\d+)/iptables/$', entity_iptables, name="entity_iptables"),
    # View for rendering zip file with iptables rules for all entities in a project.
    url(r'^project/(?P<project_id>\d+)/iptables/$', project_iptables, name="project_iptables"),
    # View for rendering zip file with iptables rules for all entities in a project for a specific location.
    url(r'^project/(?P<project_id>\d+)/location/(?P<location_id>\d+)/iptables/$', project_iptables, name="project_location_iptables"),

    # View for showing project communications in a diagram.
    url(r'^project/(?P<pk>\d+)/diagram/$', project_diagram, name="project_diagram"),

    # Views for logging-in/out the users.
    url(r'^login/$', login, {'template_name': 'conntrackt/login.html'}, name="login"),
    url(r'^logout/$', logout, name="logout"),
)
