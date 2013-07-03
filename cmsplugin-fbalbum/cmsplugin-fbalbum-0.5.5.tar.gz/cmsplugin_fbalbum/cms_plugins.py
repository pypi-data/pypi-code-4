from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _

from models import Fb
from models import PLUGIN_TEMPLATES


class FacebookAlbumPlugin(CMSPluginBase):
    model = Fb
    name = _("Facebook Album")
    render_template = PLUGIN_TEMPLATES[0][0]

    def render(self, context, instance, placeholder):
        if instance and instance.template:
            self.render_template = instance.template
        context.update({
            'object': instance,
        })
        return context

plugin_pool.register_plugin(FacebookAlbumPlugin)
