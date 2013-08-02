# coding=utf-8
from django import template
from django_helpers.helpers.templatetags import TemplateNode, parse_args
from django_helpers.apps.nivo_slider.models import NivoSlider as NivoSliderModel
from django_helpers.apps.nivo_slider import NivoSlider

__author__ = 'ajumell'


class NivoSliderNode(TemplateNode):
    def render(self, context):
        name = self.args[0].resolve(context)
        slider_obj = NivoSliderModel.objects.get(name=name)
        slider = NivoSlider()

        for attr in dir(slider_obj):
            if not attr.startswith('__'):
                if hasattr(slider, attr):
                    val = getattr(slider_obj, attr)
                    setattr(slider, attr, val)

        slider.slider_id = slider_obj.id
        for img in slider_obj.slides():
            url = img.image.url
            caption = img.caption
            alt_text = img.alternate_text
            link = img.link
            transition = img.transition
            slider.add_image(url, caption, alt_text, link, transition)
        return unicode(slider)


register = template.Library()


@register.tag
def nivo_slider(parser, token):
    bits = token.split_contents()
    args, kwargs = parse_args(bits, parser)
    return NivoSliderNode(args, kwargs)