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

from django.conf import settings
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.importlib import import_module
from django.utils.translation import ugettext_lazy as _

from configfield import params

_registry = {}


def register_block(block_class):
    block_key = '%s.%s' % (block_class.__module__, block_class.__name__)
    _registry[block_key] = {
        'label': block_class.label or block_class.name,
        'class': block_class,
    }


def get_registered_blocks():
    return _registry.items()


def get_block(block_path, placed_block=None):
    module, class_name = block_path.rsplit('.', 1)
    mod = import_module(module)
    block_class = getattr(mod, class_name)
    return block_class(placed_block)


class Block(object):
    name = 'not_defined'
    label = None
    config_params = ()  # configuration parameters, to be overriden

    def __init__(self, placed_block=None):
        self.placed_block = placed_block
        if placed_block is not None:
            self.place = placed_block.placed_at
        else:
            self.place = '_unplaced_'

    def update_context(self, context):
        pass  # to be overriden

    def render_block(self, request, template_name='block.html', block_title=None,
                     context=None):
        if context is None:
            context = {}
        block_context = {
            'block_title': block_title or self.placed_block.name,
            'place': self.place,
            'placed_block': self.placed_block,
            'block_name': self.name,
        }
        context.update(block_context)
        self.update_context(context)
        return render_to_string(template_name, context,
                                context_instance=RequestContext(request))

    def get_config(self):
        from configfield.params import ConfigDict
        return ConfigDict(self.config_params, getattr(self.placed_block, 'config', {}))

    def render(self, request, context):
        raise NotImplementedError()

    def show(self, place, request, context):
        return self.place == place


class TemplateBlock(Block):
    name = _('Template block')
    config_params = Block.config_params + (
        params.Template(
            name='template',
            default='block_skel.html',
            label=_('Template to be used for rendering this block'),
        ),
    )

    def render(self, request, context):
        template_name = self.get_config()['template'].get_value()
        return self.render_block(request, template_name, context=context)

register_block(TemplateBlock)


def autodiscover_blocks():
    import imp

    for app in settings.INSTALLED_APPS:
        try:
            app_path = import_module(app).__path__
        except AttributeError:
            continue

        # use imp.find_module to find the app's forms.py
        try:
            imp.find_module('blocks', app_path)
        except ImportError:
            continue

        # import the app's blocks.py file
        blocks_module = import_module('%s.blocks' % app)
