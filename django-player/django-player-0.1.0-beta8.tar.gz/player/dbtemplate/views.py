# Copyright (c) 2010 by Manuel Saelices
#
# This file is part of django-playerlayer.
#
# django-playerlayer is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# django-playerlayer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with django-playerlayer.  If not, see <http://www.gnu.org/licenses/>.

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _

from dbtemplates.models import Template

from player.dbtemplate.forms import TemplateAdminForm


@login_required
def template_list(request):
    """ List URLs patterns stored in database """
    templates = Template.objects.all()
    return render_to_response('dbtemplate/template_list.html',
                              {'template_list': templates},
                              context_instance=RequestContext(request))


@login_required
def template_detail(request, template_id):
    """ View a template stored in database """
    template = Template.objects.get(pk=template_id)
    return render_to_response('dbtemplate/template_detail.html', {'template': template},
                              context_instance=RequestContext(request))


@login_required
def template_add(request, template=None):
    """ Add a new template to store in database """
    if request.method == 'POST':
        form = TemplateAdminForm(request.POST, instance=template)
        if form.is_valid():
            template = form.save()
            msg = template and _(u'The template was successfully modified') or \
                  _(u'The template was successfully added')
            messages.success(request, msg)
            return HttpResponseRedirect(reverse('template_detail', args=(template.id, )))
    else:
        form = TemplateAdminForm(instance=template)
    return render_to_response(
        "dbtemplate/template_edit.html",
        {'form': form, 'template': template},
        context_instance=RequestContext(request),
    )


@login_required
def template_edit(request, template_id):
    """ Edit a template to store in database """
    template = get_object_or_404(Template, pk=template_id)
    return template_add(request, template)
