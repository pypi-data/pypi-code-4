# Copyright (c) 2010 by Yaco Sistemas
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

from django import forms

from player.base.fields import ConfigFormField
from player.base.forms import BaseForm
from player.block import get_registered_blocks, get_block
from player.block.models import PlacedBlock


class PlacedBlockForm(BaseForm, forms.ModelForm):

    class Media:
        js = ('block/js/dynamic_config_params.js', )

    def __init__(self, *args, **kwargs):
        super(PlacedBlockForm, self).__init__(*args, **kwargs)
        instance = kwargs.pop('instance', None)
        block_choices = [("", "---------")]
        block_choices.extend([(block_key, '%s (%s)' % (unicode(block['label']), block_key)) for block_key, block in get_registered_blocks()])
        old_path_field = self.fields['block_path']
        self.fields['block_path'] = forms.ChoiceField(label=old_path_field.label, choices=block_choices)
        if instance and 'config' in self.fields.keys():
            config = instance.get_block().get_config()
            if self.data:
                new_block_path = self.fields['block_path'].widget.value_from_datadict(self.data, self.files, self.add_prefix('block_path'))
                if instance.block_path != new_block_path:
                    # a uncommon situation if you changes the path selector dinamically when the block already exists
                    # we have to avoid a bad validation of config field because validate an old config_param definition
                    config = get_block(new_block_path).get_config()
            config_field = self.fields['config']
            config_field.set_config(config)

    class Meta:
        model = PlacedBlock


class AjaxPlacedBlockForm(PlacedBlockForm):

    config = ConfigFormField()

    class Meta:
        model = PlacedBlock
        fields = ('name', 'block_path', 'config')

    def save(self, *args, **kwargs):
        self.instance.placed_at = self.data.get('placed_at', None)
        blocks = PlacedBlock.objects.filter(placed_at=self.instance.placed_at).order_by('-order')
        if blocks:
            order = blocks[0].order + 1
        else:
            order = 0
        self.instance.order = order
        return super(AjaxPlacedBlockForm, self).save(*args, **kwargs)


class BlockConfigForm(forms.Form):
    config = ConfigFormField()
