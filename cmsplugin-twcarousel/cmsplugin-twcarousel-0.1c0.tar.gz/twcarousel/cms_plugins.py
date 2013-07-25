from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from .models import Carousel
from .admin import SlideInline
from django.utils.translation import ugettext as _


class CarouselPlugin(CMSPluginBase):
    model = Carousel
    name = _('Carousel Plugin')
    render_template = 'twcarousel/carousel.html'

    inlines = [
        SlideInline,
    ]

    def render(self, context, instance, placeholder):
        context.update({'instance': instance})
        return context

plugin_pool.register_plugin(CarouselPlugin)
