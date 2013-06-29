from django.core.urlresolvers import reverse
from django.template import Library
from django.utils.translation import ugettext as _

register = Library()


@register.inclusion_tag('data/delete_collection_content.html', takes_context=True)
def content_delete(context, collection, next_url=None, link_title=None, title_message=None, confirmation_message=None, action=None):
    if not confirmation_message:
        confirmation_message = _('You can not undo this action. Are you sure?')
    else:
        confirmation_message = _(confirmation_message)
    if not link_title:
        link_title = _('Remove all the content')
    else:
        link_title = _(link_title)
    if not title_message:
        title_message = _('Remove elements from collection %s') % collection._meta.verbose_name
    else:
        title_message = _(title_message)
    if not action:
        action = reverse('content_delete')
    result = {'title_message': title_message,
              'confirmation_message': confirmation_message,
              'link_title': link_title,
              'next_url': next_url,
              'action': action,
             }
    app = collection._meta.app_label
    module = 'item'
    if context['request'].user.has_perm("%s.delete_%s" % (app, module)):
        result['collection_id'] = collection.id
    return result
