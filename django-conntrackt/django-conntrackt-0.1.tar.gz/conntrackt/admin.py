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
from django.contrib import admin
from django.core.urlresolvers import resolve

# Application imports.
from .models import Project, Location, Entity, Interface, Communication


class InterfaceInline(admin.StackedInline):
    """
    This class implements the inline admin view of the Interface instances. This
    is used when adding the entities (since it's easier to specify interface for
    an entity right away).

    Properties:

      - model - Model that this admin class refers to.
      - extra - Number of interfaces that should be show inline for
        adding/editing.
    """

    model = Interface
    extra = 1


class CommunicationProjectListFilter(admin.SimpleListFilter):
    """
    This class implements a project-based filter for the communications list
    view. The filter is applied on both the source and destination field of a
    communication.

    The filter assumes that the communication belongs to a project by following
    the relationships through source and destination field towards interface,
    then entity, and then finally entity's project.

    Both source and destination must fullfil the requirement of belonging to the
    same project in order for the communication to be part of the resulting
    queryset.
    """

    # Set-up the filter title and parameter name that will be used for GET
    # request.
    title = "project"
    parameter_name = "project"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples that provide possible filter values that can be
        applied.

        Arguments:

          request - Request associated with the calling view.

          model_admin - Modem admin that can be used for accessing the model
          data.

        Returns:

          List of (project_id, project_object) tuples.
        """

        return [(p.id, p) for p in Project.objects.all()]

    def queryset(self, request, queryset):
        """
        Applies filtering by project ID on the provided communication queryset.

        Arguments:

          request - Request associated with the calling view.

          queryset - Current queryset used for displaying the information in the
          view.

        Returns:

          Queryset with applied filtering by object (if any). If no filtering
          needs to be done, returns original queryset.
        """

        # Apply the project filter on source and destination entity's project
        # ID, if it was specified.
        if self.value():
            return queryset.filter(source__entity__project=self.value(),
                                   destination__entity__project=self.value())

        return queryset


class CommunicationLocationListFilter(admin.SimpleListFilter):
    """
    This class implements a location-based filter for the communications list
    view. The filter is applied on both the source and destination field of a
    communication.

    The filter assumes that the communication belongs to a location by following
    the relationships through source and destination field towards interface,
    then entity, and then finally entity's location.

    Both source and destination must fullfil the requirement of belonging to the
    same location in order for the communication to be part of the resulting
    queryset.
    """

    # Set-up the filter title and parameter name that will be used for GET
    # request.
    title = "location"
    parameter_name = "location"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples that provide possible filter values that can be
        applied.

        Arguments:

          request - Request associated with the calling view.

          model_admin - Modem admin that can be used for accessing the model
          data.

        Returns:

          List of (project_id, project_object) tuples.
        """

        return [(p.id, p) for p in Location.objects.all()]

    def queryset(self, request, queryset):
        """
        Applies filtering by project ID on the provided communication queryset.

        Arguments:

          request - Request associated with the calling view.

          queryset - Current queryset used for displaying the information in the
          view.

        Returns:

          Queryset with applied filtering by object (if any). If no filtering
          needs to be done, returns original queryset.
        """

        # Apply the location filter on source and destination entity's project
        # ID, if it was specified.
        if self.value():
            return queryset.filter(source__entity__location=self.value(),
                                   destination__entity__location=self.value())

        return queryset


class CommunicationAdmin(admin.ModelAdmin):
    """
    Modifies the default admin class for the Communication class. The
    communication class needs to be modified in a number of ways in order to
    cater for easier adding of communication links, letting us limit the
    interfaces being shown as source/destination to specific project and/or
    site.
    """

    # Show standard fields of the model, and also include a separate edit link
    # so that other fields can be editable.
    list_display = ('source', 'destination', 'protocol', 'port', 'edit_link')
    # Make the extra edit link the main link for bringing-up admin page for
    # editing the communication.
    list_display_links = ('edit_link',)
    # All of the fields should be editable inline for ease-of-use purposes.
    list_editable = ('source', 'destination', 'protocol', 'port')
    # Add filters for project/location.
    list_filter = (CommunicationProjectListFilter, CommunicationLocationListFilter)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Overrides the default queryset for the foreign key fields. This lets us
        limit the specification of communication to specific project and/or
        location. These are in turn passed through the GET parameters.

        Arguments:

          db_field - Name of the model field for which this method is called.

          request - Request associated with the calling view.

          kwargs - Additional keyword arguments
        """

        # Resolve the view name based on the request's path.
        view_name = resolve(request.path).view_name

        # Only process the source and destination fields that point to
        # interfaces.
        if db_field.name == "source" or db_field.name == "destination":
            # Perform no filtering by default.
            interface_filter = {}

            # If project was specified in GET requests, add it as a filter.
            if 'project' in request.GET:
                interface_filter['entity__project'] = request.GET['project']
            # If location was specified in GET request, add it as a filter.
            if 'location' in request.GET:
                interface_filter['entity__location'] = request.GET['location']
            # If there are any filtering options for the show interfaces, apply them.
            if interface_filter:
                kwargs["queryset"] = Interface.objects.filter(**interface_filter)

        # Call the parent's method so it would do any of its magic.
        return super(CommunicationAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class EntityAdmin(admin.ModelAdmin):
    """
    This class implements the admin view of the entity instances. It adds some
    inline capability that can be edited for the entity, and also adds inline
    editing of interfaces related to the entity.
    """

    # Show the interfaces inline when editing an entity.
    inlines = [InterfaceInline]
    # Specify what should be viewed in a list display.
    list_display = ('name', 'project', 'location')
    # Allow the user to change project and location directly in the list.
    list_editable = ('project', 'location')
    # Enable filtering based on project and location.
    list_filter = ['project', 'location']


class InterfaceAdmin(admin.ModelAdmin):
    """
    This class implements the admin view of the interface instances. It allows
    editing the IP address and netmask of an interface directly in the listing.

    It also adds some filtering capability based on project and/or location.
    """

    # Specify fields that should be visible in the list view.
    list_display = ('entity', 'address', 'netmask')
    # Allow changing of IP address and netmask directly in the list view.
    list_editable = ('address', 'netmask')
    # Enable filtering based on project and location.
    list_filter = ['entity__project', 'entity__location']


# Register our admin classes.
admin.site.register(Project)
admin.site.register(Location)
admin.site.register(Entity, EntityAdmin)
admin.site.register(Interface, InterfaceAdmin)
admin.site.register(Communication, CommunicationAdmin)
