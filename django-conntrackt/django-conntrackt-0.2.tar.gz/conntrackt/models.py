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
from django.contrib.admin.util import NestedObjects
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.query_utils import Q

# Application imports.
from .utils import list_formatter_callback, get_distinct_colors


class SearchManager(models.Manager):
    """
    Custom model manager that implements search for model instances that contain
    a specific string (search term) in fields "name" or "description".
    """

    def search(self, search_term):
        """
        Performs a search for model instances that contain the provided search
        term in fields "name" or "description". The search is case-insensitive.

        Arguments:
          search_term - String to search the name and description for.

        Returns:
          Query set with model instances that matched the search.
        """

        return self.filter(Q(name__icontains=search_term) | Q(description__icontains=search_term))


class RelatedCollectorMixin(object):
    """
    Implements model mixin for easily obtainning related items of a model
    instance.

    The mixin can be used for obtaining all model objects that are directly or
    indirectly linked to the calling model object (through foreign key
    relationships).

    This mixin is very useful in delete views for warning the user about all of
    the related items that will be deleted if the calling item is deleted as
    well.
    """

    def get_dependant_objects(self):
        """
        Creates a list of model objects that depend (reference), both directly
        and indirectly, on calling model object. The calling model object is
        included as the first element of the list. This method call can be used
        in order to obtain a list of model objects that would get deleted in
        case the calling model object gets deleted.

        Returns:
          Nested list of model objects that depend (reference) calling model
          object.
        """

        collector = NestedObjects(using='default')

        collector.collect([self])

        return collector.nested()

    def get_dependant_objects_representation(self):
        """
        Creates a nested list of object representations that depend (reference),
        both directly and indirectly, calling model object. This method call can
        be used in order to obtain a list of string representations of model
        objects that would get deleted in case the calling model object gets
        deleted.

        The resulting nested list can be shown to the user for
        warning/notification purposes using the unordered_list template tag.

        Each non-list element will be a string generated using the
        conntrackt.utils.list_formatter_callback function.

        Returns:
          Nested list of representations of model objects that depend
          (reference) calling model object.
        """

        collector = NestedObjects(using='default')

        collector.collect([self])

        return collector.nested(list_formatter_callback)


class Project(RelatedCollectorMixin, models.Model):
    """
    Implements a model with information about a project. A project has some
    basic settings, and mainly serves the purpose of grouping entities for
    easier handling and administration.

    Fields:

      name - String denoting the project name.
      description - Free-form description of the project.
    """

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    objects = SearchManager()
    deletion_collect_models = ["Entity", "Interface"]

    class Meta:
        permissions = (("view", "Can view information"),)

    def __unicode__(self):
        """
        Returns:
          String representation of a project.
        """

        return self.name

    def get_absolute_url(self):
        """
        Return absolute URL for viewing a single project.
        """

        return reverse("project", kwargs={'pk': self.pk})

    def get_project_communications_summary(self):
        """
        Creates a list of dictionaries where each dictionary provides summary of
        a communication. Each dictionary will contain the following keys:

        - source - Source of the communication.
        - source_color - Color that is associated with the source of
          communication. The color will match with color used in the project
          communications diagram.
        - destination - Destination of the communication.
        - destination_color - Color that is associated with the destination of
          communication. The color will match with color used in the project
          communications diagram.
        - protocol - Protocol used for communication.
        - port - Port used for communication.

        Returns:
          List of dictionaries, where each dictionary describes a single communication.
        """

        # Obtain the list of colors.
        colors = get_distinct_colors(self.entity_set.count())

        # Fetch ID's of each end entity.
        entity_ids = self.entity_set.values_list("pk", flat=True).order_by("pk")

        # Map the entity ID's to generated colors.
        entity_colors = dict(zip(entity_ids, colors))

        # Set-up an empty list where the resulting data will be stored.
        communications = []

        # Process each communication, and add the information to result.
        for communication in Communication.objects.filter(source__entity__project=self).select_related():
            communications.append({"source": communication.source.entity.name,
                                   "source_color": entity_colors[communication.source.entity.pk],
                                   "destination": communication.destination.entity.name,
                                   "destination_color": entity_colors[communication.destination.entity.pk],
                                   "protocol": communication.protocol,
                                   "port": communication.port})

        # Finally return the result.
        return communications


class Location(RelatedCollectorMixin, models.Model):
    """
    Implements a model with information about location. Locations can further be
    assigned to entities, letting the user group different servers and equipment
    based on location.

    Locations are not tied to specific project, and they do not have to be
    actual physical locations. Such generic locations are therefore reusable
    accross multiple projects.

    For example, locations can be:

      - Main site
      - Backup site
      - Disaster recovery site
      - Belgrade
      - Stockholm

    Fields:

      name - String denoting the location name.
      description - Free-form description of a location.
    """

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __unicode__(self):
        """
        Returns:
          String representation of a location.
        """

        return self.name


class Entity(RelatedCollectorMixin, models.Model):
    """
    Models an entity in a project. An entity can be a server, router, or any
    other piece of networking equipment that has its own IP address.

    Entities can also be used for representing subnets etc. This is useful when
    the communication restrictions need to be applied across a subnet.

    Entities are tied to specific projects and locations.

    Fields:

      name - String denoting the entity name.
      description - Free-form description of an entity.
      project - Foreign key pointing to the project to which the entity
      belongs.
      location - Foreign key pointing to the location at which the entity is
      located.
    """

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    project = models.ForeignKey(Project)
    location = models.ForeignKey(Location)
    objects = SearchManager()

    class Meta:
        # Fix the plural form used by Django.
        verbose_name_plural = 'entities'
        # Enforce uniqueness of entity name in a project.
        unique_together = ("name", "project")

    def __unicode__(self):
        """
        Returns:
          String representation of an entity. This identifier contains name of
          entity, its project name, and location name.
        """

        return "%s (%s - %s)" % (self.name, self.project, self.location)

    def incoming_communications(self):
        """
        Returns:
          List of incoming communications for an entity.
        """

        communications = []

        for interface in self.interface_set.all():
            for communication in interface.destination_set.all():
                communications.append(communication)

        return communications

    def outgoing_communications(self):
        """
        Returns:
          List of outgoing communications for an entity.
        """

        communications = []

        for interface in self.interface_set.all():
            for communication in interface.source_set.all():
                communications.append(communication)

        return communications

    def get_absolute_url(self):
        """
        Return absolute URL for viewing a single entity.
        """

        return reverse("entity", kwargs={'pk': self.pk})

    def clean(self):
        """
        Performs additional validation checks on the submitted data. It will
        verify the following:

          - That entity is not linked to any other entity in case of project
            change.
        """

        # Perform the check if entity is being updated.
        if self.pk:
            # Fetch the old data from database.
            # @TODO: Is it better to do copying during __init__ instead?
            old_object = Entity.objects.get(pk=1)

            # Make sure that entity has no communications in current project if
            # moving it around.
            if self.project != old_object.project and (self.incoming_communications() or self.outgoing_communications()):
                raise ValidationError("The entity cannot be moved to different project as long as it has valid communications with entities in current project.")


class Interface(RelatedCollectorMixin, models.Model):
    """
    Models a representation of an interface on an entity. It can be used for
    representing the subnets as well.

    Each interface is coupled with a specific Entity.

    Fields:
      name - String denoting the interface name. For example 'eth0', 'eth1'
      etc.
      description - Free-form description of an interface.
      entity - Foreign key pointing to the entity to which the interface
      belongs.
      address - IP address of an interface. It's possible to store network
      address in it as well.
      netmask - Netmask of the interface. By default this is /32
      (255.255.255.255), but in case of subnet entities this can be used for
      denoting the network netmask.
    """

    name = models.CharField(max_length=100, default='eth0')
    description = models.TextField(blank=True, default='Main network interface.')
    entity = models.ForeignKey(Entity)
    address = models.IPAddressField()
    netmask = models.IPAddressField(default='255.255.255.255')

    class Meta:
        # Enforce uniqueness of interface name in an entity. Enforce uniqueness
        # of IP address in a subnet for an entity.
        unique_together = (("name", "entity"),
                           ("entity", "address", "netmask"),)

    def __unicode__(self):
        """
        Returns:
          String representation of an interface. In case of single IP this will
          simply be the interface name and IP address. In case of subnet it will
          include the netmask as well.
        """

        if self.netmask == '255.255.255.255':
            return '%s (%s)' % (self.entity.name, self.address)
        else:
            return '%s (%s/%s)' % (self.entity.name, self.address, self.netmask)


class Communication(RelatedCollectorMixin, models.Model):
    """
    Models a representation of allowed network communication. This lets the user
    display the possible network connections that should be allowed. Information
    from the communication instances is also used for generating the iptables
    rules for the entities.

    Communication instances allow the user to specify one of the three possible
    protocols and related information:

      - TCP, along with the TCP port.
      - UDP, along with the UDP port.
      - ICMP, along with the ICMP type.

    Allowed communication is always represented as combination of source
    interface, destination interface, protocol, and port/ICMP type.

    Fields:
      source - Foreign key to the source (originating) interface. The
      communication is expected to come _from_ the source.
      destination - Foreign key to the destination interface. The destination
      interface is expected to be able to accept incoming connections
      (i.e. entity's servers are listening on those).
      protocol - Textual field denoting the protocol that is used for
      communication. This can be 'TCP', 'UDP', or 'ICMP'.
      port - Port number used by the protocol. In case of ICMP, this is an ICMP
      type (in numeric form).
      description - Free-form text that can be used to describe the
      communication. This is also used when generating the iptables rules for
      documenting the rules.
    """

    PROTOCOL_CHOICES = (
        ('TCP', 'TCP'),
        ('UDP', 'UDP'),
        ('ICMP', 'ICMP'),
        )

    source = models.ForeignKey(Interface, related_name='source_set')
    destination = models.ForeignKey(Interface, related_name='destination_set')
    protocol = models.CharField(max_length=10, choices=PROTOCOL_CHOICES)
    port = models.IntegerField(default=0)
    description = models.TextField(blank=True)

    class Meta:
        # Enforce uniqueness of communication.
        unique_together = ("source", "destination", "protocol", "port")

    def __unicode__(self):
        """
        Returns:
          String representation of an interface. This involves showing the
          source and destination _entity_ name, protocol, and port.
        """

        return "%s -> %s (%s:%s)" % (self.source.entity.name, self.destination.entity.name, self.protocol, self.port)

    def clean(self):
        """
        Performs additional validation checks on the submitted data. It will
        verify the following:

          - That source and destination interface belongs to distinct entities.
          - That the specified protocol is supported.
        """

        if self.source.entity == self.destination.entity:
            raise ValidationError('Source and destination entities are identical.')

        if self.source.entity.project != self.destination.entity.project:
            raise ValidationError('Source and destination entities do not belong to the same project')

        if (self.protocol.upper(), self.protocol.upper()) not in self.PROTOCOL_CHOICES:
            raise ValidationError('%s is not a supported protocol.' % self.protocol)

    def edit_link(self):
        """
        This method is used for providing an additional 'Edit' link in the admin
        site for the communication instances (for the display_list).

        This provides ability to let all of the other fields of a communication
        instance to be editable.
        """

        return "Edit"

    def source_representation(self):
        """
        Produces string representation of communication that includes only the
        source interface information.

        The method is useful where the destination context is well known.

        Returns:
            Communication representation that includes only information about
            the source interface.
        """

        return "%s - %s: %d" % (self.source, self.protocol, self.port)

    def destination_representation(self):
        """
        Produces string representation of communication that includes only the
        destination interface information.

        The method is useful where the source context is well known.

        Returns:
            Communication representation that includes only information about
            the destination interface.
        """

        return "%s - %s: %d" % (self.destination, self.protocol, self.port)
