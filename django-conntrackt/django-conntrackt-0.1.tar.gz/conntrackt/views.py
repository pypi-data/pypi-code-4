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

# Django imports.
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic import TemplateView, DetailView, CreateView, UpdateView, DeleteView

# Third-party application imports.
from braces.views import MultiplePermissionsRequiredMixin, SetHeadlineMixin

# Application imports.
from .forms import ProjectForm, LocationForm, EntityForm, InterfaceForm, CommunicationForm
from .models import Project, Entity, Location, Interface, Communication
from .utils import generate_entity_iptables, generate_project_diagram


class RedirectToNextMixin(object):
    """
    View mixin that can be used for redirecting the user to URL defined through
    a GET parameter. The mixin is usable with Create/Update/Delete views that
    utilise the get_success_url() call.

    The mixin accepts the following class options:

        next_parameter - Name of the GET parameter that contains the redirect
        URL. Defaults to "next".
    """

    next_parameter = "next"

    def get_success_url(self):
        """
        Returns the success URL to which the user will be redirected.
        """

        return self.request.GET.get(self.next_parameter, super(RedirectToNextMixin, self).get_success_url())


class IndexView(MultiplePermissionsRequiredMixin, TemplateView):
    """
    Custom view used for rendering the index page.
    """

    template_name = 'conntrackt/index.html'

    # Required permissions.
    permissions = {
        "all": ("conntrackt.view",),
        }
    # Raise authorisation denied exception for unmet permissions.
    raise_exception = True

    def get_context_data(self, **kwargs):
        """
        Returns the context data that should be used for rendering of the
        template.

        Adds the 'projects' context object containing all of the projects
        available sorted aplhabetically by name.
        """

        # Set the context using the parent class.
        context = super(IndexView, self).get_context_data(**kwargs)

        # Store information about all projcts in context.
        context['projects'] = Project.objects.all().order_by('name')

        # Store information about all locations in context.
        context['locations'] = Location.objects.all().order_by('name')

        return context


class ProjectView(MultiplePermissionsRequiredMixin, DetailView):
    """
    Custom view for presenting the project information.
    """

    model = Project

    permissions = {
        "all": ("conntrackt.view",),
        }
    # Raise authorisation denied exception for unmet permissions.
    raise_exception = True

    def get_context_data(self, **kwargs):
        """
        Returns the context data that should be used for rendering of the
        template.

        Adds the 'location_entities' context object that contains tuples of the
        form '(location, entities)', where location is an instance of a
        Location, and entities is a query set of entities that belong to that
        particular location, and to related project.
        """

        # Set the context using the parent class.
        context = super(ProjectView, self).get_context_data(**kwargs)

        # Set-up an array that will contaion (location, entities) tuples.
        location_entities = []

        # Add the (location, entities) tuple for each location that has entities
        # belonging to the related project.
        for location in Location.objects.filter(entity__project=self.object).distinct().order_by("name"):
            entities = Entity.objects.filter(project=self.object, location=location)
            location_entities.append((location, entities))

        # Add the (location, entities) tuples to context.
        context['location_entities'] = location_entities

        # Finally return the context.
        return context


class EntityView(MultiplePermissionsRequiredMixin, DetailView):
    """
    Custom view for presenting entity information.
    """

    # Optimise the query to fetch the related data from reverse relationships.
    queryset = Entity.objects.all()
    queryset = queryset.prefetch_related('interface_set__destination_set__source__entity')
    queryset = queryset.prefetch_related('interface_set__destination_set__destination__entity')
    queryset = queryset.prefetch_related('interface_set__source_set__source__entity')
    queryset = queryset.prefetch_related('interface_set__source_set__destination__entity')

    # Required permissions.
    permissions = {
        "all": ("conntrackt.view",),
        }
    # Raise authorisation denied exception for unmet permissions.
    raise_exception = True

    def get_context_data(self, **kwargs):
        """
        Returns the context data that should be used for rendering of the
        template.

        Adds the 'entity_iptables' context object that contains full iptables
        rules generated for the entity.
        """

        # Call the parent class method.
        context = super(EntityView, self).get_context_data(**kwargs)

        # Add the rendered iptables rules to the context.
        context['entity_iptables'] = generate_entity_iptables(self.object)

        # Add the incoming and outgoing commmunication to the context.
        context["incoming_communications"] = self.object.incoming_communications()
        context["outgoing_communications"] = self.object.outgoing_communications()

        # Add the interfaces to the context.
        context["interfaces"] = self.object.interface_set.all().order_by("name")

        # Add project/location to the context.
        context["project"] = self.object.project
        context["location"] = self.object.location

        return context


@permission_required("conntrackt.view", raise_exception=True)
def entity_iptables(request, pk):
    """
    Custom view that returns response containing iptables rules generated for an
    entity.

    Makes sure to set the Content-Disposition of a response in order to
    signal the browser it should start download of this view's response
    immediately. Also sets the suggested filename for it.

    Arguments:

        pk - Primary key of the Entity object for which the rules should be
        generated.

    Returns:

        Response object that contains the iptables rules for specified entity.
    """

    # Fetch the entity, and construct the response with iptables rules as
    # content.
    entity = get_object_or_404(Entity, pk=pk)
    content = generate_entity_iptables(entity)
    response = HttpResponse(content, mimetype='text/plain')

    # Add the Content-Disposition information for the browser, telling the
    # browser to download the file with suggested filename.
    response['Content-Disposition'] = "attachment; filename=%s-iptables.conf" % entity.name.lower().replace(" ", "_")

    return response


@permission_required("conntrackt.view", raise_exception=True)
def project_iptables(request, project_id, location_id=None):
    """
    Custom view for obtaining iptables for all entities of a project or project
    location in a single ZIP file.

    Arguments:

        request - Request object.

        project_id - Unique ID of the project for whose entities the iptables
        rules should be generated.

        location_id - Optional unique ID of the project location for whose
        entities the iptables rules should be generated. Default is None, which
        means generate rules for _all_ entities in a project.

    Returns:

        Response object that contains the ZIP file and Content-Disposition
        information.
    """

    # Fetch the project.
    project = get_object_or_404(Project, pk=project_id)

    # Set-up a string IO object to which we'll write the ZIP file (in-memory).
    buff = StringIO()

    # Create a new ZIP file in-memory.
    zipped_iptables = ZipFile(buff, "w", ZIP_DEFLATED)

    # Create the response object, setting the mime type so browser could offer
    # to open the file with program as well.
    response = HttpResponse(mimetype='application/zip')

    # If specific location was specified, get the entities that are part of that
    # project location only, otherwise fetch all of the project's entities. Also
    # set-up the filename that will be suggested to the browser.
    if location_id:
        location = get_object_or_404(Location, pk=location_id)
        entities = project.entity_set.filter(location=location)
        filename = '%s-%s-iptables.zip' % (project.name.lower().replace(" ", "_"), location.name.lower().replace(" ", "_"))
    else:
        entities = project.entity_set.all()
        filename = '%s-iptables.zip' % (project.name.lower().replace(" ", "_"))

    # Render iptables rules for each entity, placing them in the ZIP archive.
    for entity in entities:
        entity_iptables = generate_entity_iptables(entity)
        zipped_iptables.writestr("%s-iptables.conf" % entity.name.lower().replace(" ", "_"), entity_iptables)

    # Close the archive, and flush the buffer.
    zipped_iptables.close()
    buff.flush()

    # Write the contents of our buffer (ZIP archive) to response content, and
    # close the IO string.
    response.write(buff.getvalue())
    buff.close()

    # Set the Content-Disposition so the browser would know it should download
    # the archive, and suggest the filename.
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename

    # Finally return the response object.
    return response


class ProjectCreateView(RedirectToNextMixin, SetHeadlineMixin, MultiplePermissionsRequiredMixin, CreateView):
    """
    View for creating a new project.
    """

    model = Project
    form_class = ProjectForm
    headline = "Add new project"
    template_name = "conntrackt/create_form.html"

    # Required permissions.
    permissions = {
        "all": ("conntrackt.add_project",),
        }

    # Raise authorisation denied exception for unmet permissions.
    raise_exception = True


class ProjectUpdateView(RedirectToNextMixin, SetHeadlineMixin, MultiplePermissionsRequiredMixin, UpdateView):
    """
    View for modifying an existing project.
    """

    model = Project
    form_class = ProjectForm
    template_name = "conntrackt/update_form.html"

    # Required permissions.
    permissions = {
        "all": ("conntrackt.change_project",),
        }

    # Raise authorisation denied exception for unmet permissions.
    raise_exception = True

    def get_headline(self):
        """
        Set headline based on project name.
        """

        return "Update project %s" % self.object.name


class ProjectDeleteView(RedirectToNextMixin, SetHeadlineMixin, MultiplePermissionsRequiredMixin, DeleteView):
    """
    View for deleting a project.
    """

    model = Project
    template_name = "conntrackt/delete_form.html"

    # Required permissions.
    permissions = {
        "all": ("conntrackt.delete_project",),
        }

    # Raise authorisation denied exception for unmet permissions.
    raise_exception = True

    success_url = reverse_lazy("index")

    def post(self, *args, **kwargs):
        """
        Add a success message that will be displayed to the user to confirm the
        project deletion.
        """

        messages.success(self.request, "Project %s has been removed." % self.get_object().name, extra_tags="alert alert-success")

        return super(ProjectDeleteView, self).post(*args, **kwargs)

    def get_headline(self):
        """
        Set headline based on project name.
        """

        return "Delete project %s" % self.object.name


class LocationCreateView(RedirectToNextMixin, SetHeadlineMixin, MultiplePermissionsRequiredMixin, CreateView):
    """
    View for creating a new location.
    """

    model = Location
    form_class = LocationForm
    headline = "Add new location"
    template_name = "conntrackt/create_form.html"

    # Required permissions.
    permissions = {
        "all": ("conntrackt.add_location",),
        }

    # Raise authorisation denied exception for unmet permissions.
    raise_exception = True

    success_url = reverse_lazy("index")


class LocationUpdateView(RedirectToNextMixin, SetHeadlineMixin, MultiplePermissionsRequiredMixin, UpdateView):
    """
    View for modifying an existing location.
    """

    model = Location
    form_class = LocationForm
    template_name = "conntrackt/update_form.html"

    # Required permissions.
    permissions = {
        "all": ("conntrackt.change_location",),
        }

    # Raise authorisation denied exception for unmet permissions.
    raise_exception = True

    success_url = reverse_lazy("index")

    def get_headline(self):
        """
        Set headline based on location name.
        """

        return "Update location %s" % self.object.name


class LocationDeleteView(RedirectToNextMixin, SetHeadlineMixin, MultiplePermissionsRequiredMixin, DeleteView):
    """
    View for deleting a location.
    """

    model = Location
    template_name = "conntrackt/delete_form.html"

    # Required permissions.
    permissions = {
        "all": ("conntrackt.delete_location",),
        }

    # Raise authorisation denied exception for unmet permissions.
    raise_exception = True

    success_url = reverse_lazy("index")

    def post(self, *args, **kwargs):
        """
        Add a success message that will be displayed to the user to confirm the
        location deletion.
        """

        messages.success(self.request, "Location %s has been removed." % self.get_object().name, extra_tags="alert alert-success")

        return super(LocationDeleteView, self).post(*args, **kwargs)

    def get_headline(self):
        """
        Set headline based on location name.
        """

        return "Delete location %s" % self.object.name


class EntityCreateView(RedirectToNextMixin, SetHeadlineMixin, MultiplePermissionsRequiredMixin, CreateView):
    """
    View for creating a new entity.
    """

    model = Entity
    form_class = EntityForm
    headline = "Add new entity"
    template_name = "conntrackt/create_form.html"

    # Required permissions.
    permissions = {
        "all": ("conntrackt.add_entity",),
        }

    # Raise authorisation denied exception for unmet permissions.
    raise_exception = True

    def get_form(self, form_class):
        """
        Returns an instance of form that can be used by the view.

        The method will limit the project or location select inputs if request
        contained this information.
        """

        form = super(EntityCreateView, self).get_form(form_class)

        # Limit the project selection if required.
        project_id = self.request.GET.get("project", None)
        if project_id:
            form.fields["project"].queryset = Project.objects.filter(pk=project_id)
            form.fields["project"].widget.attrs["readonly"] = True

        # Limit the location selection if required.
        location_id = self.request.GET.get("location", None)
        if location_id:
            form.fields["location"].queryset = Location.objects.filter(pk=location_id)
            form.fields["location"].widget.attrs["readonly"] = True

        return form

    def get_initial(self):
        """
        Returns initial values that should be pre-selected (if they were
        specified through a GET parameter).
        """

        initial = super(EntityCreateView, self).get_initial()

        initial["project"] = self.request.GET.get("project", None)
        initial["location"] = self.request.GET.get("location", None)

        return initial


class EntityUpdateView(RedirectToNextMixin, SetHeadlineMixin, MultiplePermissionsRequiredMixin, UpdateView):
    """
    View for updating an existing entity.
    """

    model = Entity
    form_class = EntityForm
    template_name = "conntrackt/update_form.html"

    # Required permissions.
    permissions = {
        "all": ("conntrackt.change_entity",),
        }

    # Raise authorisation denied exception for unmet permissions.
    raise_exception = True

    def get_headline(self):
        """
        Set headline based on entity name.
        """

        return "Update entity %s" % self.object.name


class EntityDeleteView(RedirectToNextMixin, SetHeadlineMixin, MultiplePermissionsRequiredMixin, DeleteView):
    """
    View for deleting an entity.
    """

    model = Entity
    template_name = "conntrackt/delete_form.html"

    # Required permissions.
    permissions = {
        "all": ("conntrackt.delete_entity",),
        }

    # Raise authorisation denied exception for unmet permissions.
    raise_exception = True

    def post(self, *args, **kwargs):
        """
        Add a success message that will be displayed to the user to confirm the
        entity deletion.
        """

        messages.success(self.request, "Entity %s has been removed." % self.get_object().name, extra_tags="alert alert-success")

        return super(EntityDeleteView, self).post(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Deletes the object. This method is overridden in order to obtain the
        project ID for success URL.

        @TODO: Fix this once Django 1.6 comes out with fix from ticket 19044.
        """

        self.success_url = reverse("project", args=(self.get_object().project.id,))

        return super(EntityDeleteView, self).delete(*args, **kwargs)

    def get_headline(self):
        """
        Set headline based on entity name.
        """

        return "Delete entity %s" % self.object.name


class InterfaceCreateView(RedirectToNextMixin, SetHeadlineMixin, MultiplePermissionsRequiredMixin, CreateView):
    """
    View for creating a new interface.
    """

    model = Interface
    form_class = InterfaceForm
    headline = "Add new interface"
    template_name = "conntrackt/create_form.html"

    # Required permissions
    permissions = {
        "all": ("conntrackt.add_interface",),
        }

    # Raise authorisation denied exception for unmet permissions.
    raise_exception = True

    def get_form(self, form_class):
        """
        Returns an instance of form that can be used by the view.

        The method will limit the entity select input if request contained this
        information.
        """

        form = super(InterfaceCreateView, self).get_form(form_class)

        # Limit the entity selection if required.
        entity_id = self.request.GET.get("entity", None)
        if entity_id:
            form.fields["entity"].queryset = Entity.objects.filter(pk=entity_id)
            form.fields["entity"].widget.attrs["readonly"] = True

        return form

    def get_initial(self):
        """
        Returns initial values that should be pre-selected (if they were
        specified through a GET parameter).
        """

        initial = super(InterfaceCreateView, self).get_initial()

        initial["entity"] = self.request.GET.get("entity", None)

        return initial

    def get_success_url(self):
        """
        Returns the URL to which the user should be redirected after an
        interface has been created.

        The URL in this case will be set to entity's details page.
        """

        return reverse("entity", args=(self.object.entity.pk,))


class InterfaceUpdateView(RedirectToNextMixin, SetHeadlineMixin, MultiplePermissionsRequiredMixin, UpdateView):
    """
    View for updating an existing interface.
    """

    model = Interface
    form_class = InterfaceForm
    template_name = "conntrackt/update_form.html"

    # Required permissions.
    permissions = {
        "all": ("conntrackt.change_interface",),
        }

    # Raise authorisation denied exception for unmet permissions.
    raise_exception = True

    def get_form(self, form_class):
        """
        Returns an instance of form that can be used by the view.

        The method will limit the entities that can be selected for the
        interface to the ones that belong to the same project as the currently
        set entity.
        """

        form = super(InterfaceUpdateView, self).get_form(form_class)

        # Limit the entities to same project.
        form.fields["entity"].queryset = Entity.objects.filter(project=self.object.entity.project)

        return form

    def get_success_url(self):
        """
        Returns the URL to which the user should be redirected after an
        interface has been updated.

        The URL in this case will be set to entity's details page.
        """

        return reverse("entity", args=(self.object.entity.pk,))

    def get_headline(self):
        """
        Set headline based on interface name.
        """

        return "Update interface %s" % self.object.name


class InterfaceDeleteView(RedirectToNextMixin, SetHeadlineMixin, MultiplePermissionsRequiredMixin, DeleteView):
    """
    View for deleting an interface.
    """

    model = Interface
    template_name = "conntrackt/delete_form.html"

    # Required permissions.
    permissions = {
        "all": ("conntrackt.delete_interface",),
        }

    # Raise authorisation denied exception for unmet permissions.
    raise_exception = True

    def post(self, *args, **kwargs):
        """
        Add a success message that will be displayed to the user to confirm the
        interface deletion.
        """

        messages.success(self.request, "Interface %s has been removed." % self.get_object().name, extra_tags="alert alert-success")

        return super(InterfaceDeleteView, self).post(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Deletes the object. This method is overridden in order to obtain the
        entity ID for success URL.

        @TODO: Fix this once Django 1.6 comes out with fix from ticket 19044.
        """

        self.success_url = reverse("entity", args=(self.get_object().entity.id,))

        return super(InterfaceDeleteView, self).delete(*args, **kwargs)

    def get_headline(self):
        """
        Set headline based on interface name.
        """

        return "Delete interface %s" % self.object.name


class CommunicationCreateView(RedirectToNextMixin, SetHeadlineMixin, MultiplePermissionsRequiredMixin, CreateView):
    """
    View for creating a new communication.
    """

    model = Communication
    form_class = CommunicationForm
    headline = "Add new communication"
    template_name = "conntrackt/create_form.html"

    # Required permissions
    permissions = {
        "all": ("conntrackt.add_communication",),
        }

    # Raise authorisation denied exception for unmet permissions.
    raise_exception = True

    def get_form(self, form_class):
        """
        Returns an instance of form that can be used by the view.

        The method will limit the source and destination interface selection to
        interfaces belonging to the same project as provided entity ID (if any
        was provided).
        """

        form = super(CommunicationCreateView, self).get_form(form_class)

        # Limit the interface selection based on provided source entity,
        # destination entity, or project.
        entity_id = self.request.GET.get("from_entity", None) or self.request.GET.get("to_entity", None)
        project_id = self.request.GET.get("project", None)

        if project_id:
            form.fields["source"].queryset = Interface.objects.filter(entity__project=project_id)
            form.fields["destination"].queryset = Interface.objects.filter(entity__project=project_id)
        elif entity_id:
            entity = Entity.objects.get(pk=1)
            form.fields["source"].queryset = Interface.objects.filter(entity__project=entity.project)
            form.fields["destination"].queryset = Interface.objects.filter(entity__project=entity.project)

        return form

    def get_initial(self):
        """
        Returns initial values that should be pre-selected (if they were
        specified through a GET parameter).
        """

        initial = super(CommunicationCreateView, self).get_initial()

        # If source or destination entity were specified in request, fetch the
        # first interface from them and use it as initial source and destination.
        from_entity = self.request.GET.get("from_entity", None)
        to_entity = self.request.GET.get("to_entity", None)

        if from_entity:
            try:
                interface = Interface.objects.filter(entity=from_entity)[0]
                initial["source"] = interface.id
            except IndexError:
                pass

        if to_entity:
            try:
                interface = Interface.objects.filter(entity=to_entity)[0]
                initial["destination"] = interface.id
            except IndexError:
                pass

        return initial

    def get_success_url(self):
        """
        Returns the URL to which the user should be redirected after a
        communication has been created.

        The URL will either point to value provided via GET parameter "next", or
        to project page to which the communication belongs.
        """

        # We must set the success URL to something first.
        self.success_url = reverse("project", args=(self.object.source.entity.project.pk,))

        # This will override the URL if parameter "next" was provided (from
        # RedirectToNextMixin).
        success_url = super(CommunicationCreateView, self).get_success_url()

        return success_url


class CommunicationUpdateView(RedirectToNextMixin, SetHeadlineMixin, MultiplePermissionsRequiredMixin, UpdateView):
    """
    View for updating an existing communication.
    """

    model = Communication
    form_class = CommunicationForm
    template_name = "conntrackt/update_form.html"

    # Required permissions.
    permissions = {
        "all": ("conntrackt.change_communication",),
        }

    # Raise authorisation denied exception for unmet permissions.
    raise_exception = True

    def get_form(self, form_class):
        """
        Returns an instance of form that can be used by the view.

        The method will limit the source and destination interfaces that can be
        selected for the communication. Both will be limited to interfaces
        coming from entities that belong to the same project as current
        communication's source interface.
        """

        form = super(CommunicationUpdateView, self).get_form(form_class)

        project = self.object.source.entity.project

        form.fields["source"].queryset = Interface.objects.filter(entity__project=project)
        form.fields["destination"].queryset = Interface.objects.filter(entity__project=project)

        return form

    def get_success_url(self):
        """
        Returns the URL to which the user should be redirected after a
        communication has been created.

        The URL will either point to value provided via GET parameter "next", or
        to project page to which the communication belongs.
        """

        return self.request.GET.get("next", reverse("project", args=(self.object.source.entity.project.pk,)))

    def get_headline(self):
        """
        Set headline based on communication.
        """

        return "Update communication %s" % self.object


class CommunicationDeleteView(RedirectToNextMixin, SetHeadlineMixin, MultiplePermissionsRequiredMixin, DeleteView):
    """
    View for deleting an communication.
    """

    model = Communication
    template_name = "conntrackt/delete_form.html"

    # Required permissions.
    permissions = {
        "all": ("conntrackt.delete_communication",),
        }

    # Raise authorisation denied exception for unmet permissions.
    raise_exception = True

    def post(self, *args, **kwargs):
        """
        Add a success message that will be displayed to the user to confirm the
        communication deletion.
        """

        messages.success(self.request, "Communication %s has been removed." % self.get_object(), extra_tags="alert alert-success")

        return super(CommunicationDeleteView, self).post(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Deletes the object. This method is overridden in order to obtain the
        entity ID for success URL.

        @TODO: Fix this once Django 1.6 comes out with fix from ticket 19044.
        """

        entity_id = self.request.GET.get("from_entity", None) or self.request.GET.get("to_entity", None) or self.get_object().source.entity.pk

        self.success_url = reverse("entity", args=(entity_id,))

        return super(CommunicationDeleteView, self).delete(*args, **kwargs)

    def get_headline(self):
        """
        Set headline based on communication.
        """

        return "Delete communication %s" % self.object


@permission_required("conntrackt.view", raise_exception=True)
def project_diagram(request, pk):
    """
    Custom view that returns response containing diagram of project
    communications.

    The diagram will include coloured entities, with directional lines
    connecting the source and destination end entities.

    The output format is SVG.

    Arguments:

        request - Request object.

        pk - Project ID for which the diagram should be generated.

    Returns:

        Response object that contains the project diagram rendered as SVG.
    """

    # Fetch the project.
    project = get_object_or_404(Project, pk=pk)

    # Generate the diagram.
    content = generate_project_diagram(project).create_svg()

    # Set the mime type.
    response = HttpResponse(content, mimetype='image/svg+xml')

    # Return the response object.
    return response
