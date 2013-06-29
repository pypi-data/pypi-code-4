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

from dbresolver.forms import URLPatternForm
from dbresolver.models import URLPattern


@login_required
def url_list(request):
    """ List URLs patterns stored in database """
    urlpatterns = URLPattern.objects.all()
    return render_to_response('dburl/url_list.html', {'url_list': urlpatterns},
                              context_instance=RequestContext(request))


@login_required
def url_detail(request, url_id):
    """ View a URL pattern stored in database """
    url = URLPattern.objects.get(pk=url_id)
    return render_to_response('dburl/url_detail.html', {'url': url},
                              context_instance=RequestContext(request))


@login_required
def url_add(request, url=None):
    """ Add a new URL pattern to store in database """
    if request.method == 'POST':
        form = URLPatternForm(request.POST, instance=url)
        if form.is_valid():
            url = form.save()
            msg = url and _(u'The URL was successfully modified') or \
                  _(u'The URL was successfully added')
            messages.success(request, msg)
            return HttpResponseRedirect(reverse('url_detail', args=(url.id, )))
    else:
        form = URLPatternForm(instance=url)
    return render_to_response(
        "dburl/url_edit.html",
        {'form': form, 'url': url},
        context_instance=RequestContext(request),
    )


@login_required
def url_edit(request, url_id):
    """ Edit a URL pattern to store in database """
    url = get_object_or_404(URLPattern, pk=url_id)
    return url_add(request, url)
