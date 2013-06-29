from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.template import Library
from django.utils.translation import ugettext as _

register = Library()


@register.inclusion_tag('manage/generic_delete.html', takes_context=True)
def generic_delete(context, content, next_url=None, link_title=None, title_message=None, confirmation_message=None, action=None):
    if not confirmation_message:
        confirmation_message = _('You can not undo this action. Are you sure?')
    else:
        confirmation_message = _(confirmation_message)
    if not link_title:
        link_title = _('Remove this item')
    else:
        link_title = _(link_title)
    if not title_message:
        title_message = _('Remove %(model)s') % {'model': content._meta.verbose_name}
    else:
        title_message = _(title_message)
    if not action:
        action = reverse('generic_delete')
    result = {'title_message': title_message,
              'confirmation_message': confirmation_message,
              'link_title': link_title,
              'next_url': next_url,
              'action': action,
             }
    app = content._meta.app_label
    module = content._meta.module_name
    if context['request'].user.has_perm("%s.delete_%s" % (app, module)):
        content_type = ContentType.objects.get(app_label=app, model=module)
        result['content_id'] = content.id
        result['content_type_id'] = content_type.id
    return result
