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
from django.core.context_processors import csrf
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.simplejson import dumps
from django.utils.translation import ugettext as _

from player.block import get_block
from player.block.forms import BlockConfigForm, PlacedBlockForm, AjaxPlacedBlockForm
from player.block.models import PlacedBlock


@login_required
def block_list(request):
    """ List blocks in website """
    blocks = PlacedBlock.objects.all()
    return render_to_response('block/block_list.html',
                              {'block_list': blocks},
                              context_instance=RequestContext(request))


@login_required
def block_detail(request, block_id):
    """ View a template stored in database """
    block = PlacedBlock.objects.get(pk=block_id)
    return render_to_response('block/block_detail.html', {'placed_block': block},
                              context_instance=RequestContext(request))


@login_required
def block_add(request, block=None):
    """ Add a new block to place in website """
    if request.method == 'POST':
        form = PlacedBlockForm(request.POST, instance=block)
        if form.is_valid():
            block = form.save()
            msg = block and _(u'The block was successfully modified') or \
                  _(u'The block was successfully added')
            messages.success(request, msg)
            return HttpResponseRedirect(reverse('block_detail', args=(block.id, )))
    else:
        form = PlacedBlockForm(instance=block)
    return render_to_response(
        "block/block_edit.html",
        {'form': form, 'placed_block': block},
        context_instance=RequestContext(request),
    )


@login_required
def block_edit(request, block_id):
    """ Edit a placed block """
    block = get_object_or_404(PlacedBlock, pk=block_id)
    return block_add(request, block)


@login_required
def blocks_reorder(request):
    if not request.user.is_staff:
        return PermissionDenied()

    def relocate_blocks(items, cls):
        for order, item in enumerate(items):
            if "#" in item:
                item_split = item.split("#")
                element_id = int(item_split[0])
                placed_at = item_split[1]
                try:
                    cls.objects.get(id=element_id,
                                    placed_at=placed_at,
                                    order=order)
                except cls.DoesNotExist:
                    element = cls.objects.get(id=element_id)
                    element.order = order
                    element.placed_at = placed_at
                    element.save()

    mimetype = "application/json"
    if request.is_ajax() and request.POST and "new_order" in request.POST:
        new_order = request.POST['new_order']
        items = new_order.split(",")
        relocate_blocks(items, PlacedBlock)
        return HttpResponse(dumps(True), mimetype=mimetype)
    return HttpResponseBadRequest(mimetype=mimetype)


@login_required
def generate_blocks_configuration(request, block_id):
    if not request.user.is_staff:
        raise PermissionDenied()
    placed_block = PlacedBlock.objects.get(id=block_id)
    block = placed_block.get_block()
    config = block.get_config()
    if request.method == 'POST':
        form = BlockConfigForm(request.POST)
        form.fields['config'].set_config(config)
        if form.is_valid():
            placed_block.config = form.cleaned_data['config']
            placed_block.save()
            return HttpResponse('ok')
    else:
        form = BlockConfigForm()
        form.fields['config'].set_config(config)
    context = {
        'form': form,
        'placed_block': placed_block,
        'block': block,
    }
    context.update(csrf(request))
    return render_to_response('block/block_config.html', context)


@login_required
def generate_blocks_configuration_by_path(request, block_path):
    block = get_block(block_path)
    form = BlockConfigForm()
    config = block.get_config()
    form.fields['config'].set_config(config)
    context = {
        'form': form,
        'block': block,
    }
    context.update(csrf(request))
    return render_to_response('block/block_config_by_path.html', context)


@login_required
def get_block_config(request):
    block_path = request.GET.get('block_path', '')
    block = get_block(block_path)
    form = BlockConfigForm()
    config = block.get_config()
    form.fields['config'].set_config(config)
    context = {
            'form': form,
    }
    return render_to_response('block/block_ajax_edit_config.html', context)
    

@login_required
def ajax_block_add(request):
    """ Add a new block """
    if request.method == 'POST':
        form = AjaxPlacedBlockForm(request.POST)
        block = get_block(request.POST.get('block_path', ''))
        config = block.get_config()
        form.fields['config'].set_config(config)
        if form.is_valid():
            block = form.save()
            return HttpResponse(dumps({'html': block.render(request, {}), 'success': True}),
                                mimetype='text/plain')
    else:
        form = AjaxPlacedBlockForm()
    html = render_to_string("block/block_ajax_edit.html", {'form': form },
                            context_instance=RequestContext(request),
                           )
    return HttpResponse(dumps({'html': html, 'success': False}), mimetype='text/plain')
