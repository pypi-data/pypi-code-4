from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _
from simplemenu.models import SimpleMenuPlugin as SimpleMenuPluginModel
from simplemenu.models import Link


class CMSPluginSimpleMenu(CMSPluginBase):
    model = SimpleMenuPluginModel
    name = _("Simple Menu")
    render_template = "simplemenu/plugin.html"
    module = _("TheHerk")

    def render(self, context, instance, placeholder):
        links = Link.objects.filter(simplemenu__name=instance.simplemenu).order_by('title')
        context.update({
            'instance': instance,
            'links': links,
            'placeholder': placeholder,
        })
        return context

plugin_pool.register_plugin(CMSPluginSimpleMenu)
