from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext as _
from updates.models import UpdatesPlugin as UpdatesPluginModel
from updates.models import Update


class UpdatesPlugin(CMSPluginBase):
    model = UpdatesPluginModel
    name = _("Updates")
    render_template = "updates/plugin.html"
    module = _("TheHerk")

    def render(self, context, instance, placeholder):
        updates = Update.objects.all().order_by('-date')[:instance.number_to_show]
        context.update({
            'instance': instance,
            'updates': updates,
            'placeholder': placeholder,
        })
        return context

plugin_pool.register_plugin(UpdatesPlugin)
