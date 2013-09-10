from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .models import Section


class SectionPlugin(CMSPluginBase):
    model = Section
    name = "Section"

    def render(self, context, instance, placeholder):
        if instance.enabled:
            context.update({'section': instance, 'placeholder': placeholder})
        return context

plugin_pool.register_plugin(SectionPlugin)
