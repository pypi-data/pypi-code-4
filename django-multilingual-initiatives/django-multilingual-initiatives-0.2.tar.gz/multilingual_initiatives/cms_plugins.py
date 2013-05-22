"""django-cms plugins for the ``multilingual_initiatives`` app."""
from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .models import InitiativePluginModel


class InitiativePlugin(CMSPluginBase):
    model = InitiativePluginModel
    name = _('Initiative Plugin')
    render_template = 'multilingual_initiatives/initiative_plugin.html'

    def render(self, context, instance, placeholder):
        context.update({
            'plugin': instance,
            'initiative': instance.initiative,
            'display_type': instance.display_type,
        })
        return context


plugin_pool.register_plugin(InitiativePlugin)
