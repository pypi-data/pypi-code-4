from django import template
from django.utils.translation import ugettext as _

register = template.Library()


@register.inclusion_tag('data/get_collection_status.html',
                        takes_context=True)
def get_collection_status(context, collection):
    img_base = '%smanage/img/' % context['STATIC_URL']
    if collection.is_publishable():
        alt = _('Yes')
        img = 'step-done_16.png'
    else:
        alt = _('No')
        img = 'step-undone_16.png'
    img_path = '%s%s' % (img_base, img)
    return {'path': img_path, 'alt': alt}
